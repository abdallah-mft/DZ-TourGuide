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
from rest_framework.throttling import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.password_validation import validate_password
import random 
import threading
from django.db import transaction

User = get_user_model()

OTP_EXP_SECONDS = getattr(settings, "EMAIL_VERIFICATION_EXPIRY_SECONDS", 900)
CACHE_PREFIX = "otp_"
ATTEMPT_PREFIX = "attempt_"
RESET_PREFIX = "reset_"


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.message,
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            
            print(f"Failed to send email: {e}")

def generate_otp():
    
    return f"{random.randint(100000, 999999)}" 

class RegisterView(APIView):
    throttle_classes = [AnonRateThrottle] 
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        
        existing_user = User.objects.filter(email=email).first()
        if existing_user and existing_user.is_verified:
            return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        try:
            with transaction.atomic():
                if existing_user and not existing_user.is_verified:
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

                
                
                EmailThread(
                    subject="Verify your account",
                    message=f"Your verification code is: {otp}",
                    recipient_list=[user.email]
                ).start()

            return Response({
                "message": "User registered. Please verify your email.",
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": "An error occurred during registration."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"{CACHE_PREFIX}{email}"
        cached_otp = cache.get(cache_key)

        if not cached_otp:
            return Response({"detail": "OTP expired or invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if str(cached_otp) != str(otp): 
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
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


class LogoutView(APIView): 
    permission_classes = [permissions.IsAuthenticated]
    def post (self , request ):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e :
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"detail": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"{CACHE_PREFIX}{user.email}"
        attempt_key = f"{ATTEMPT_PREFIX}{user.email}"
        cache.delete(cache_key)
        cache.delete(attempt_key)
        
        otp = generate_otp()
        cache.set(cache_key, otp, timeout=OTP_EXP_SECONDS)

        
        EmailThread(
            subject="Verify your account",
            message=f"Your new verification code is: {otp}",
            recipient_list=[user.email]
        ).start()

        return Response({"message": "New OTP sent successfully."}, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = request.data.get('email', '').lower()
        
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                return Response({"detail": "Please verify your email first."}, status=400)
            
            otp = generate_otp()
            cache_key = f"{RESET_PREFIX}{email}"
            cache.set(cache_key, otp, timeout=OTP_EXP_SECONDS)
            
            
            EmailThread(
                subject="Password Reset Code",
                message=f"Your password reset code is: {otp}\n\nThis code expires in 15 minutes.",
                recipient_list=[user.email]
            ).start()
            
        except User.DoesNotExist:
            
            pass
        
        return Response({"detail": "If the email exists, a reset code has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = request.data.get('email', '').lower()
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({"detail": "email, otp, and new_password are required."}, status=400)

        cache_key = f"{RESET_PREFIX}{email}"
        cached_otp = cache.get(cache_key)

        if not cached_otp or str(cached_otp) != str(otp):
            return Response({"detail": "Invalid or expired OTP."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": e.messages}, status=400)

        user.set_password(new_password)
        user.save(update_fields=['password'])
        cache.delete(cache_key)
        
        return Response({"detail": "Password reset successful."})

