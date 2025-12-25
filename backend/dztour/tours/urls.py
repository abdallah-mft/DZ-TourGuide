from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TourViewSet, BookingViewSet, create_booking

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'', TourViewSet, basename='tour')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:tour_id>/book/', create_booking, name='create-booking'),
]