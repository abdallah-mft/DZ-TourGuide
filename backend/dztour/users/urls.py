from django.urls import path 
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', LoginView.as_view(), name='token_obtain'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='me'),
]