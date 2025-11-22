from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
import random
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model


User = get_user_model()

OTP_EXP_SECONDS = getattr(settings, "EMAIL_VERIFICATION_EXPIRY_SECONDS", 900)
CACHE_PREFIX = "otp_"

def generate_otp():
    return f"{random.randint(1000, 9999)}"

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        existing_user = User.objects.filter(email=email).first()
        
        if existing_user:
            if existing_user.is_verified:
                return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = existing_user
        else:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        cache_key = f"{CACHE_PREFIX}{user.email}"
        cache.set(cache_key, otp, timeout=OTP_EXP_SECONDS)

        
        try:
            send_mail(
                subject="Verify your account",
                message=f"Your verification code is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"detail": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "User registered. Please verify your email.",
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"{CACHE_PREFIX}{email}"
        cached_otp = cache.get(cache_key)

        if not cached_otp:
            return Response({"detail": "OTP expired or invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            user = User.objects.get(email=email)
            user.is_verified = True
            user.save()
            
            
            cache.delete(cache_key)

            
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Email verified successfully.",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    def patch(self, request):
        s = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

