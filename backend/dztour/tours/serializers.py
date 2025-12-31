from rest_framework import serializers
from django.utils import timezone
from opencage.geocoder import OpenCageGeocode, RateLimitExceededError, InvalidInputError
import os

from .models import Tour, TourPicture, Booking, CustomTour
from guides.models import Wilaya
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
        read_only_fields = ['guide', 'price', 'average_rating', 'review_count', 'wilaya']

    def validate(self, attrs):
        ''' 
        check if the given (lang/lat) strat position match the guide covered
        commune and wilaya, using externel api of OpenCage
        '''
        lat = attrs.get('start_point_latitude')
        lng = attrs.get('start_point_longitude')
        if not lat or not lng:
            print('lat lang not exist')
            return attrs

        key = os.getenv('OPEN_CAGE_KEY')
        if not key:
            print('key not exist')
            return attrs

        try:
            geocoder = OpenCageGeocode(key)
            results = geocoder.reverse_geocode(float(lat), float(lng), no_annotations=1)
            if not results or len(results) == 0:
                print('no resault')
                return attrs

            components = results[0]['components']            
            commune_name = components.get('_normalized_city') or components.get('city') or components.get('town')
            state_name = components.get('state')
            
            if not commune_name and not state_name:
                print('no commune or state provided in geolocation components')
                return attrs

            # Automatically set the wilaya based on state_name
            if state_name:
                try:
                    wilaya_obj = Wilaya.objects.get(name_fr__iexact=state_name)
                    attrs['wilaya'] = wilaya_obj
                except Wilaya.DoesNotExist:
                    print(f"Wilaya with name {state_name} not found in database")

            request = self.context.get('request')
            if request and hasattr(request.user, 'profile'):
                guide_profile = request.user.profile
                
                if commune_name:
                    if not guide_profile.commune_covered.filter(name_fr__iexact=commune_name).exists():
                        raise serializers.ValidationError({"start_point": f"The location ({commune_name}) is not in your covered communes."})
                elif state_name:
                    if not guide_profile.wilaya_covered.filter(name_fr__iexact=state_name).exists():
                        raise serializers.ValidationError({"start_point": f"The wilaya ({state_name}) is not in your covered wilayas."})
        
        except (RateLimitExceededError, InvalidInputError) as ex:
            print(f"OpenCage Validation Skipped: {ex}")
            pass

        return attrs

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
        read_only_fields = ('tour', 'custom_tour', 'tourist', 'status', 'created_at', 'updated_at', 'tour_type')

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