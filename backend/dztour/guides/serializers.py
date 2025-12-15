from rest_framework import serializers
from .models import GuideProfile
from ..users.serializers import UserSerializer

class GuideProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = GuideProfile
        fields = '__all__'