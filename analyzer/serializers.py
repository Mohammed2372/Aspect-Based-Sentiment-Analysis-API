from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


from .models import AspectResult, AnalysisRecord, AnalysisSession


class AspectResultSerializer(ModelSerializer):
    class Meta:
        model = AspectResult
        fields = ["aspect", "sentiment", "confidence"]


class AnalysisRecordSerializer(serializers.ModelSerializer):
    results = AspectResultSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisRecord
        fields = ["original_text", "results"]


class AnalysisSessionSerializer(serializers.ModelSerializer):
    # Explicitly define inputs so the Form shows them
    csv_file = serializers.FileField(write_only=True, required=False)
    text = serializers.CharField(
        write_only=True, required=False, source="raw_input_text"
    )

    class Meta:
        model = AnalysisSession
        fields = [
            "id",
            "session_type",
            "created_at",
            "status",
            "total_items",
            "csv_file",
            "text",
        ]
        read_only_fields = ["id", "session_type", "created_at", "status", "total_items"]


class SessionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisSession
        fields = ["id", "session_type", "status", "created_at", "total_items"]


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
