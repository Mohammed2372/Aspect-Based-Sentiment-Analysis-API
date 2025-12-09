from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ReviewAnalysisView,
    UserHistoryView,
    RegisterView,
    BulkUploadView,
    BulkStatusView,
)

urlpatterns = [
    # App Endpoints
    path("analyze/", ReviewAnalysisView.as_view(), name="analyze-review"),
    path("history/", UserHistoryView.as_view(), name="user-history"),
    # Auth Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Bulk Upload Endpoints
    path("bulk-upload/", BulkUploadView.as_view(), name="bulk-upload"),
    path("bulk-status/<int:file_id>/", BulkStatusView.as_view(), name="bulk-status"),
]
