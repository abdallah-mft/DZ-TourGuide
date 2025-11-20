from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
import cloudinary.uploader
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , min_length=8)
    
    class Meta:
        model = User 
        fields  = ('email', 'first_name', 'last_name', 'role', 'phone', 'password','profile_picture')

    def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone', 'created_at' , 'profile_picture')
        read_only_fields = ('id', 'created_at')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'profile_picture')
    def validate_profile_picture(self,value):
        if value.size > 5 * 1024 * 1024 :
            raise serializers.ValidationError("Image file is too large ( >5MB ) ")
        valid_extensions = ['jpg','jpeg','png','gif','webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
        return value 
    def update(self, instance, validated_data):
        if 'profile_picture' in validated_data and instance.profile_picture:
            old_public_id = getattr(instance.profile_picture, 'public_id', None)
            if not old_public_id:
                old_name = str(instance.profile_picture)
                old_public_id = os.path.splitext(old_name)[0]
            if old_public_id:
                result = cloudinary.uploader.destroy(
                    old_public_id,
                    invalidate=True,
                    resource_type='image'
                )
                print(f"Cloudinary destroy result: {result}")
        return super().update(instance, validated_data)
        
        return super().update(instance, validated_data)   
        
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


