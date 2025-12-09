from django.contrib.auth.models import User
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


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
