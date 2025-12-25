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

    def validate_start_point_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_start_point_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value

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


class UpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['date_time', 'number_of_participants']
    
    def validate_date_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("The booking date cannot be in the past.")
        return value
    
    def validate(self, attrs):
        if self.instance and self.instance.status not in ['pending', 'negotiated']:
            raise serializers.ValidationError("Cannot update a booking that has been accepted, rejected, or cancelled.")
        return attrs