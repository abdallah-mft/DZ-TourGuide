from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/verify/', VerifyEmailView.as_view(), name='verify_email'),
    path('token/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='me'),
    path('logout/',LogoutView.as_view() , name='logout'),
    path('register/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
]