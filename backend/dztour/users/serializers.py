import os
import cloudinary.uploader                       
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'role', 'phone', 'password', 'profile_picture')

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format.")
        return value.lower()

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        parts = full_name.split(' ', 1)
        validated_data['first_name'] = parts[0]
        validated_data['last_name'] = parts[1] if len(parts) > 1 else ''
        
        user = User.objects.create_user(**validated_data)
        user.is_verified = False
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'phone', 'created_at', 'profile_picture', 'is_active')
        read_only_fields = ('id', 'created_at', 'is_active')
    
    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()


class UserUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ('full_name', 'phone', 'profile_picture')

    def update(self, instance, validated_data):
        full_name = validated_data.pop('full_name', None)
        if full_name:
            parts = full_name.split(' ', 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ''
        
        if 'profile_picture' in validated_data and instance.profile_picture:
            old_public_id = getattr(instance.profile_picture, 'public_id', None)
            if not old_public_id:
                old_name = str(instance.profile_picture)
                old_public_id = os.path.splitext(old_name)[0]
            if old_public_id:
                cloudinary.uploader.destroy(old_public_id, invalidate=True, resource_type='image')
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs.get('email'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified. Please verify your account first.")
            
        attrs['user'] = user
        return attrs


