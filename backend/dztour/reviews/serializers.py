from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer
from tours.serializers import MinimalBookingSerializer

class ReviewSerializer(serializers.ModelSerializer):
    tourist = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['tourist', 'guide', 'created_at']

    def validate_booking(self, value):
        user = self.context['request'].user
        if value.tourist != user:
            raise serializers.ValidationError("You can only review your own bookings.")
        
        if value.status != 'accepted':
            raise serializers.ValidationError("You can only review accepted bookings.")

        if not self.instance and Review.objects.filter(booking=value).exists():
             raise serializers.ValidationError("You have already reviewed this booking.")
    
        return value

    def validate(self, attrs):
        tour_rating = attrs.get('tour_rating')
        guide_rating = attrs.get('guide_rating')
        comment = attrs.get('comment')

        if self.instance:
            if tour_rating is None:
                tour_rating = self.instance.tour_rating
            if guide_rating is None:
                guide_rating = self.instance.guide_rating
            if comment is None:
                comment = self.instance.comment

        if not tour_rating and not guide_rating and not comment:
            raise serializers.ValidationError("A review must have at least a rating (tour/guide) or a comment.")
        
        return attrs

class ReviewWithBookingSerializer(ReviewSerializer):
    booking = MinimalBookingSerializer(read_only=True)
