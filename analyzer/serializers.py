from rest_framework import serializers
from rest_framework.serializers import Serializer


class ReviewSerializer(Serializer):
    text = serializers.CharField(
        min_length=5, max_length=1000, help_text="The review text to analyze"
    )
