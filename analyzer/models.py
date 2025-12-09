from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AnalysisSession(models.Model):
    SESSION_TYPES = [("TEXT", "Raw Text"), ("FILE", "CSV File")]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES)
    csv_file = models.FileField(upload_to="uploads/", null=True, blank=True)
    raw_input_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    total_items = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Session {self.id} ({self.session_type})"


class AnalysisRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    session = models.ForeignKey(
        AnalysisSession, related_name="records", on_delete=models.CASCADE
    )
    original_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class AspectResult(models.Model):
    record = models.ForeignKey(
        AnalysisRecord, related_name="results", on_delete=models.CASCADE
    )
    aspect = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()

    def __str__(self) -> str:
        return f"{self.aspect}: {self.sentiment}"
