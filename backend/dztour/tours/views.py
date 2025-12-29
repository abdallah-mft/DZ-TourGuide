from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from django.db.models import Case, When, Value, IntegerField, Q
from django.shortcuts import get_object_or_404

from .models import Tour, TourPicture, Booking, CustomTour
from .serializers import TourSerializer, TourPictureSerializer, DetailedBookingSerializer, MinimalBookingSerializer, UpdateBookingSerializer, CustomTourSerializer
from .permissions import IsTheGuideOwnerOrReadOnly

class TourViewSet(viewsets.ModelViewSet):
    serializer_class = TourSerializer
    permission_classes = [IsTheGuideOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'guide__user__username']

    def get_queryset(self):
        queryset = Tour.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        wilaya = self.request.query_params.get('wilaya')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_duration:
            queryset = queryset.filter(duration__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)
        if wilaya:
            queryset = queryset.filter(wilaya__code=wilaya)

        return queryset

    def perform_create(self, serializer):
        serializer.save(guide=self.request.user.profile)  

    @action(detail=False, methods=['GET'], url_path='for-guide')
    def list_guide_tours(self, request):
        guide = request.user.profile
        tours = Tour.objects.filter(guide=guide)
        serializer = TourSerializer(tours, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['DELETE'], url_path='delete-image/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        image = get_object_or_404(TourPicture, id=image_id)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], url_path='add-images')
    def add_images(self, request, pk=None):
        tour = Booking.get_or_404(pk=pk)
        images = request.FILES.getlist('images')

        if not images:
            return Response({"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uploaded_data = []
            for g in images:
                serializer = TourPictureSerializer(data={'image': g})
                if serializer.is_valid(raise_exception=True):
                    serializer.save(tour=tour)
                    uploaded_data.append(serializer.data)

            return Response({
                "status": "Images uploaded successfully",
                "tour_id": tour.id,
                "count": len(uploaded_data),
                "images": uploaded_data
            }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class BookingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailedBookingSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateBookingSerializer
        return MinimalBookingSerializer

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(tourist=user) | Q(tour__guide__user=user) | Q(custom_tour__guide__user=user)
        ).select_related('tour', 'tourist', 'tour__guide', 'custom_tour').annotate(
            status_priority=Case(
                When(status='negotiated', then=Value(1)),
                When(status='pending', then=Value(2)),
                When(status='accepted', then=Value(3)),
                When(status='rejected', then=Value(4)),
                When(status='cancelled', then=Value(5)),
                default=Value(6),
                output_field=IntegerField(),
            )
        ).order_by('status_priority', '-updated_at')

    def perform_update(self, serializer):
        booking = self.get_object()
        if self.request.user != booking.tourist:
            raise permissions.PermissionDenied("Only the tourist who created this booking can update it.")
        serializer.save()

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        
        if request.user != booking.get_tour_object().guide.user:
            return Response({"error": "Only the guide can accept this booking"}, status=status.HTTP_403_FORBIDDEN)
            
        if booking.status not in ['pending', 'negotiated']:
            return Response({"error": f"Cannot accept a booking with status: {booking.status}"}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'accepted'
        booking.save()
        return Response({"message": "Booking accepted successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        
        if request.user != booking.get_tour_object().guide.user:
            return Response({"error": "Only the guide can reject this booking"}, status=status.HTTP_403_FORBIDDEN)
            
        if booking.status not in ['pending', 'negotiated']:
            return Response({"error": f"Cannot reject a booking with status: {booking.status}"}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'rejected'
        booking.save()
        return Response({"message": "Booking rejected successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        
        if request.user != booking.tourist:
            return Response({"error": "Only the tourist can cancel their booking"}, status=status.HTTP_403_FORBIDDEN)
            
        if booking.status in ['rejected', 'cancelled']:
            return Response({"error": "Booking is already cancelled or rejected"}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'cancelled'
        booking.save()
        return Response({"message": "Booking cancelled successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='suggest-new-date')
    def suggest_new_date(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)

        if request.user != booking.get_tour_object().guide.user and request.user != booking.tourist:
            return Response({"error": "Only the guide or the tourist can suggest a new date"}, status=status.HTTP_403_FORBIDDEN)
        
        if booking.status in ['accepted', 'rejected', 'cancelled']:
            return Response({"error": "Cannot negotiate a closed booking"}, status=status.HTTP_400_BAD_REQUEST)
            
        new_date = request.data.get('date_time')
        if not new_date:
            return Response({"error": "Date is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(booking, data={'date_time': new_date}, partial=True)
        serializer.is_valid(raise_exception=True)
            
        booking.date_time = serializer.validated_data['date_time']
        booking.status = 'negotiated'
        booking.save()
        return Response({"message": "New date suggested successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_regular_booking(request, tour_id):
    if request.user.role != 'tourist':
        return Response({"error": "Only tourists can book tours"}, status=status.HTTP_403_FORBIDDEN)

    tour = get_object_or_404(Tour, pk=tour_id)
    serializer = DetailedBookingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(tour=tour, tourist=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_custom_tour_booking(request):
    if request.user.role != 'tourist':
        return Response({"error": "Only tourists can create custom tours"}, status=status.HTTP_403_FORBIDDEN)
    
    with transaction.atomic():
        # Step 1: Create the custom tour
        custom_tour_data = {
            'title': request.data.get('title'),
            'description': request.data.get('description'),
            'wilaya': request.data.get('wilaya'),
            'start_point_latitude': request.data.get('start_point_latitude'),
            'start_point_longitude': request.data.get('start_point_longitude'),
            'budget': request.data.get('budget'),
            'guide': request.data.get('guide'),
        }
        
        custom_tour_serializer = CustomTourSerializer(data=custom_tour_data)
        custom_tour_serializer.is_valid(raise_exception=True)
        custom_tour = custom_tour_serializer.save(tourist=request.user)
        
        # Step 2: Create a booking for the custom tour
        booking_data = {
            'date_time': request.data.get('date_time'),
            'number_of_participants': request.data.get('number_of_participants', 1),
        }
        
        booking_serializer = DetailedBookingSerializer(data=booking_data)
        booking_serializer.is_valid(raise_exception=True)
        booking = booking_serializer.save(
            custom_tour=custom_tour,
            tourist=request.user
        )
        
        # Return both custom tour and booking information
        return Response({
            "message": "Custom tour and booking created successfully",
            "custom_tour": custom_tour_serializer.data,
            "booking": DetailedBookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_guide_custom_tours(request):
    if request.user.role != 'guide':
        return Response({"error": "Only guides can view their custom tour requests"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        guide_profile = request.user.profile
    except AttributeError:
        return Response({"error": "User has no guide profile"}, status=status.HTTP_400_BAD_REQUEST)

    custom_tours = CustomTour.objects.filter(guide=guide_profile).order_by('-created_at')
    serializer = CustomTourSerializer(custom_tours, many=True)
    return Response(serializer.data)
