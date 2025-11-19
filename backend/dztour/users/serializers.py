from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , min_length=8)
    
    class Meta:
        model = User 
        fields  = ('email', 'first_name', 'last_name', 'role', 'phone', 'password')

    def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone', 'created_at')
        read_only_fields = ('id', 'created_at')
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self,attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)
        
        if not user: 
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User is not active")

        attrs['user'] = user
        return attrs
