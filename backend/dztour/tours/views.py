from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Tour, TourPicture
from .serializers import TourSerializer, TourPictureSerializer
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
        tour = self.get_object()
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
    