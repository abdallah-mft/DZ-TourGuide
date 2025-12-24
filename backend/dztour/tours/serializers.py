from rest_framework import serializers
from .models import Tour, TourPicture
from users.serializers import UserSerializer

class TourPictureSerializer(serializers.ModelSerializer):
    tour = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = TourPicture
        fields = '__all__'

class TourSerializer(serializers.ModelSerializer):
    guide = UserSerializer(source='guide.user', read_only=True)
    pictures = TourPictureSerializer(many=True, read_only=True)

    class Meta:
        model = Tour
        fields = '__all__'
        read_only_fields = ['guide', 'price']