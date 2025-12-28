from rest_framework import serializers





class MostBookedTourSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    bookings = serializers.IntegerField()





class DashboardStatsSerializer(serializers.Serializer):
    
    total_bookings = serializers.IntegerField()
    accepted_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()

    
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)

    
    total_tours = serializers.IntegerField()
    tours_with_bookings = serializers.IntegerField()
    most_booked_tour = MostBookedTourSerializer(allow_null=True)





class EarningsItemSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    tour_title = serializers.CharField()
    tourist_name = serializers.CharField()
    date_time = serializers.DateTimeField()
    participants = serializers.IntegerField()
    earnings = serializers.DecimalField(max_digits=10, decimal_places=2)


class EarningsSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    breakdown = EarningsItemSerializer(many=True)





class UpcomingBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tour_title = serializers.CharField()
    tourist_name = serializers.CharField()
    date_time = serializers.DateTimeField()
    participants = serializers.IntegerField()
