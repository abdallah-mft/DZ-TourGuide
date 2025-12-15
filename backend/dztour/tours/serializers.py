from rest_framework import serializers
from .models import Tour, TourPicture
from ..guides.serializers import GuideProfileSerializer

class TourPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPicture
        fields = '__all__'

class TourSerializer(serializers.ModelSerializer):
    guide = GuideProfileSerializer(read_only=True)
    pictures = TourPictureSerializer(many=True, read_only=True)

    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ['guide', 'price']