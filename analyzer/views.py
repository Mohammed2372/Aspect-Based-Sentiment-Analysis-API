from typing import NoReturn
from django.db.models.manager import BaseManager
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination


from .models import AspectResult, AnalysisSession, AnalysisRecord
from .serializers import (
    AnalysisRecordSerializer,
    UserRegistrationSerializer,
    SessionDetailSerializer,
    AnalysisSessionSerializer,
)
from .services import ABSAService
from .tasks import process_bulk_file


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class BulkResultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class AnalysisSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self) -> BaseManager[AnalysisSession]:
        return AnalysisSession.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_serializer_class(
        self,
    ) -> SessionDetailSerializer | AnalysisSessionSerializer:
        if self.action == "retrieve":
            return SessionDetailSerializer
        return AnalysisSessionSerializer

    def create(self, request, *args, **kwargs) -> Response:
        if "csv_file" in request.FILES:
            csv_file = request.FILES["csv_file"]

            session = AnalysisSession.objects.create(
                user=request.user,
                session_type="FILE",
                csv_file=csv_file,
                status="Pending",
                total_items=0,
            )

            process_bulk_file.delay(session.id)

            serializer = AnalysisSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif "text" in request.data:
            text = request.data["text"]

            session = AnalysisSession.objects.create(
                user=request.user,
                session_type="TEXT",
                raw_input_text=text,
                status="Pending",
                total_items=1,
            )

            self._process_text_snc(session, text)

            serializer = AnalysisSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {
                    "error": "Please provide either 'csv_file' (file) or 'text' (string)."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs) -> NoReturn:
        session = self.get_object()

        # get session records
        records = session.records.all().order_by("id")

        # paginate records
        paginator = BulkResultPagination()
        paginated_records = paginator.paginate_queryset(records, request)

        # serialize records
        record_serializer = AnalysisRecordSerializer(paginated_records, many=True)

        # serialize session data
        session_data = SessionDetailSerializer(session).data
        session_data["records"] = record_serializer.data

        return paginator.get_paginated_response(session_data)

    # --- Helper Method --- #
    def _process_text_snc(self, session: AnalysisSession, text: str) -> None:
        try:
            # run AI logic
            ai_result = ABSAService.analyze_sentiment(text)

            # create record linked to session
            record = AnalysisRecord.objects.create(
                session=session,
                user=session.user,
                original_text=text,
            )

            # create aspects
            aspects = [
                AspectResult(
                    record=record,
                    aspect=item["aspect"],
                    sentiment=item["sentiment"],
                    confidence=item["confidence"],
                )
                for item in ai_result["analysis"]
            ]
            AspectResult.objects.bulk_create(aspects)

            # update session status
            session.status = "Completed"
            session.save()

        except Exception as e:
            session.status = f"Failed: {str(e)}"
            session.save()
