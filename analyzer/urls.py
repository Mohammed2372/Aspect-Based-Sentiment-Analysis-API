from django.urls import path
from .views import ReviewAnalysisView

urlpatterns = [
    path("analyze/", ReviewAnalysisView.as_view(), name="analyze-review"),
]
