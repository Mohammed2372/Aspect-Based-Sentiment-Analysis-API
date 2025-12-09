from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .models import AspectResult
from .serializers import ReviewSerializer, AnalysisRecord, AnalysisHistorySerializer
from .services import ABSAService


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
