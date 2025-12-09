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
