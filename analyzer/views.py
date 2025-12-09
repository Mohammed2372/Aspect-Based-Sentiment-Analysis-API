from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import ReviewSerializer
from .services import ABSAService


# Create your views here.
class ReviewAnalysisView(APIView):
    def post(self, request) -> Response:
        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # get data
        text = serializer.validated_data["text"]

        try:
            # call service layer
            result = ABSAService.analyze_sentiment(text)

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
