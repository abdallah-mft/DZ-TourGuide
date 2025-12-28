from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Sum, Avg, Count, F, Q
from django.utils import timezone

from tours.models import Booking, Tour
from guides.models import GuideProfile
from guides.views import IsGuideUser

from .serializers import (
    DashboardStatsSerializer,
    EarningsSerializer,
    UpcomingBookingSerializer
)


class GuideDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsGuideUser]

    def list(self, request):
        try:
            guide_profile = request.user.profile
        except GuideProfile.DoesNotExist:
            return Response(
                {"detail": "Guide profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # --------------------
        # BOOKING STATS
        # --------------------
        base_q = Q(tour__guide=guide_profile) | Q(custom_tour__guide=guide_profile)

        aggs = Booking.objects.filter(base_q).aggregate(
            total_bookings=Count('id'),
            accepted_bookings=Count('id', filter=Q(status='accepted')),
            pending_bookings=Count('id', filter=Q(status='pending')),
        )

        # --------------------
        # EARNINGS
        # --------------------
        earnings = (
            Booking.objects
            .filter(tour__guide=guide_profile, status='accepted')
            .aggregate(total=Sum(F('tour__price')))
            .get('total')
            or Decimal('0.00')
        )

        # --------------------
        # REVIEWS
        # --------------------
        total_reviews = getattr(guide_profile, 'review_count', None)
        average_rating = getattr(guide_profile, 'average_rating', None)

        if total_reviews is None or average_rating is None:
            from reviews.models import Review
            total_reviews = Review.objects.filter(guide=request.user).count()
            average_rating = (
                Review.objects
                .filter(guide=request.user)
                .aggregate(avg=Avg('guide_rating'))
                .get('avg')
                or 0
            )

        # --------------------
        # TOUR STATS (NEW)
        # --------------------
        total_tours = Tour.objects.filter(guide=guide_profile).count()

        tours_with_bookings = (
            Tour.objects
            .filter(guide=guide_profile, bookings__isnull=False)
            .distinct()
            .count()
        )

        most_booked = (
            Tour.objects
            .filter(guide=guide_profile)
            .annotate(
                bookings_count=Count(
                    'bookings',
                    filter=Q(bookings__status='accepted')
                )
            )
            .order_by('-bookings_count')
            .first()
        )

        most_booked_tour = None
        if most_booked and most_booked.bookings_count > 0:
            most_booked_tour = {
                'id': most_booked.id,
                'title': most_booked.title,
                'bookings': most_booked.bookings_count,
            }

        # --------------------
        # RESPONSE DATA
        # --------------------
        data = {
            # bookings
            'total_bookings': aggs.get('total_bookings', 0) or 0,
            'accepted_bookings': aggs.get('accepted_bookings', 0) or 0,
            'pending_bookings': aggs.get('pending_bookings', 0) or 0,

            # earnings & reviews
            'total_earnings': earnings,
            'total_reviews': total_reviews or 0,
            'average_rating': round(float(average_rating or 0), 2),

            # tours
            'total_tours': total_tours,
            'tours_with_bookings': tours_with_bookings,
            'most_booked_tour': most_booked_tour,
        }

        serializer = DashboardStatsSerializer(instance=data)
        return Response(serializer.data)

    # ==========================================================
    # EARNINGS BREAKDOWN
    # ==========================================================
    @action(detail=False, methods=['get'])
    def earnings(self, request):
        try:
            guide_profile = request.user.profile
        except GuideProfile.DoesNotExist:
            return Response(
                {"detail": "Guide profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        qs = (
            Booking.objects
            .filter(tour__guide=guide_profile, status='accepted')
            .select_related('tour', 'tourist')
            .order_by('-date_time')
        )

        limit = request.query_params.get('limit')
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass

        breakdown = []
        total = Decimal('0.00')

        for b in qs:
            price = b.tour.price or Decimal('0.00')
            total += price
            breakdown.append({
                'booking_id': b.id,
                'tour_title': b.tour.title,
                'tourist_name': f"{b.tourist.first_name or ''} {b.tourist.last_name or ''}".strip(),
                'date_time': b.date_time,
                'participants': b.number_of_participants,
                'earnings': price,
            })

        serializer = EarningsSerializer(
            instance={'total_earnings': total, 'breakdown': breakdown}
        )
        return Response(serializer.data)

    # ==========================================================
    # UPCOMING BOOKINGS
    # ==========================================================
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        try:
            guide_profile = request.user.profile
        except GuideProfile.DoesNotExist:
            return Response(
                {"detail": "Guide profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()
        qs = (
            Booking.objects
            .filter(
                (Q(tour__guide=guide_profile) | Q(custom_tour__guide=guide_profile)),
                status='accepted',
                date_time__gt=now
            )
            .select_related('tour', 'custom_tour', 'tourist')
            .order_by('date_time')
        )

        limit = request.query_params.get('limit')
        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass

        data = []
        for b in qs:
            tour_obj = b.tour or b.custom_tour
            data.append({
                'id': b.id,
                'tour_title': tour_obj.title if tour_obj else '',
                'tourist_name': f"{b.tourist.first_name or ''} {b.tourist.last_name or ''}".strip(),
                'date_time': b.date_time,
                'participants': b.number_of_participants,
            })

        serializer = UpcomingBookingSerializer(instance=data, many=True)
        return Response(serializer.data)
