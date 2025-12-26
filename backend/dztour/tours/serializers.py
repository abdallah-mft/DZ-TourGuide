from rest_framework import serializers
from django.utils import timezone
from .models import Tour, TourPicture, Booking, CustomTour
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

class CustomTourSerializer(serializers.ModelSerializer):
    tourist = UserSerializer(read_only=True)

    class Meta:
        model = CustomTour
        fields = '__all__'
        read_only_fields = ['tourist', 'created_at', 'updated_at']

    def validate_start_point_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_start_point_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.guide and instance.guide.user:
            representation['guide'] = UserSerializer(instance.guide.user).data
        else:
            representation['guide'] = None
        return representation

class DetailedBookingSerializer(serializers.ModelSerializer):
    tourist = UserSerializer(read_only=True)
    tour = serializers.SerializerMethodField()
    tour_type = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tour', 'custom_tour', 'tourist', 'status', 'created_at', 'updated_at')

    def get_tour(self, obj):
        tour_obj = obj.get_tour_object()
        if tour_obj:
            if isinstance(tour_obj, Tour):
                return TourSerializer(tour_obj).data
            elif isinstance(tour_obj, CustomTour):
                return CustomTourSerializer(tour_obj).data
        return None

    def get_tour_type(self, obj):
        return 'custom' if obj.is_custom_tour else 'regular'

class MinimalBookingSerializer(serializers.ModelSerializer):
    tourist = serializers.SerializerMethodField()
    tour_title = serializers.SerializerMethodField()
    tour_type = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('tour', 'custom_tour', 'tourist', 'status', 'created_at', 'updated_at')

    def get_tour_title(self, obj):
        tour = obj.get_tour_object()
        return tour.title

    def get_tourist(self, obj):
        if obj.tourist:
            return f"{obj.tourist.first_name} {obj.tourist.last_name}".strip() or obj.tourist.email
        return None

    def get_tour_type(self, obj):
        return 'custom' if obj.is_custom_tour else 'regular'

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