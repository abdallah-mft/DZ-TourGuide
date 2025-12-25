from rest_framework import serializers
from django.utils import timezone
from .models import Tour, TourPicture, Booking
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

class DetailedBookingSerializer(serializers.ModelSerializer):
    tour = TourSerializer(read_only=True)
    tourist = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tour', 'tourist', 'status', 'created_at', 'updated_at')


class MinimalBookingSerializer(serializers.ModelSerializer):
    tour = serializers.CharField(source='tour.title', read_only=True)
    tourist = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tour', 'tourist', 'status', 'created_at', 'updated_at')

    def get_tourist(self, obj):
        if obj.tourist:
            return f"{obj.tourist.first_name} {obj.tourist.last_name}".strip() or obj.tourist.email
        return None

    def validate_date_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("The booking date cannot be in the past.")
        return value