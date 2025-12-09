from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer


from .models import AspectResult, AnalysisRecord


class ReviewSerializer(Serializer):
    text = serializers.CharField(
        min_length=5, max_length=1000, help_text="The review text to analyze"
    )


class AspectResultSerializer(ModelSerializer):
    class Meta:
        model = AspectResult
        fields = ["aspect", "sentiment", "confidence"]


class AnalysisHistorySerializer(ModelSerializer):
    results = AspectResultSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisRecord
        fields = ["id", "original_text", "created_at", "results"]
