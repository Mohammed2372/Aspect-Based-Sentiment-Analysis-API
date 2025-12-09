from django.urls import path
from .views import ReviewAnalysisView, UserHistoryView

urlpatterns = [
    path("analyze/", ReviewAnalysisView.as_view(), name="analyze-review"),
    path("history/", UserHistoryView.as_view(), name="user-history"),
]
