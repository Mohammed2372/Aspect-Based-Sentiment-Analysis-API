from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from .views import AnalysisSessionViewSet, RegisterView

# create router
router = DefaultRouter()
router.register(r"sessions", AnalysisSessionViewSet, basename="session")


urlpatterns = [
    # Auth Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Unified API (handle actions for files and text)
    path("", include(router.urls)),
]
