from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser


from .models import AspectResult, FileUpload
from .serializers import (
    ReviewSerializer,
    AnalysisRecord,
    AnalysisHistorySerializer,
    UserRegistrationSerializer,
    FileUploadSerializer,
)
from .services import ABSAService
from .tasks import process_bulk_file


# Create your views here.
class ReviewAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # get data
        text = serializer.validated_data["text"]

        try:
            # run AI logic
            ai_responses = ABSAService.analyze_sentiment(text)

            # save
            record = AnalysisRecord.objects.create(
                user=request.user, original_text=text
            )

            # Bulk create aspect results
            bulk_aspect_objects = [
                AspectResult(
                    record=record,
                    aspect=item["aspect"],
                    sentiment=item["sentiment"],
                    confidence=item["confidence"],
                )
                for item in ai_responses["analysis"]
            ]

            AspectResult.objects.bulk_create(bulk_aspect_objects)

            return Response(ai_responses, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        history = AnalysisRecord.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        serializer = AnalysisHistorySerializer(history, many=True)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class BulkUploadView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = FileUploadSerializer

    def post(self, request) -> Response:
        uploaded_file = request.FILES.get("csv_file") or request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file attached"}, status=400)

        # create db entry
        serializer = FileUploadSerializer(data={"csv_file": uploaded_file})
        if serializer.is_valid():
            upload_instance = serializer.save(user=request.user)
            # send to celery (async)
            process_bulk_file.delay(upload_instance.id)

            return Response(
                {
                    "message": "File accepted. Processing in background",
                    "data": serializer.data,
                    "status_url": f"/api/bulk-status/{upload_instance.id}/",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, file_id) -> Response:
        try:
            upload = get_object_or_404(FileUpload, id=file_id, user=request.user)
            serializer = FileUploadSerializer(upload)

            response_data = serializer.data
            response_data["progress_display"] = (
                f"{upload.processed_rows}/{upload.total_rows}"
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except FileUpload.DoesNotExist:
            return Response(
                {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
            )
