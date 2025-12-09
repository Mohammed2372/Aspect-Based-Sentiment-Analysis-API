from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AnalysisRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
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


class FileUpload(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploads")
    csv_file = models.FileField(upload_to="bulk_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"File {self.id} {self.status}"
