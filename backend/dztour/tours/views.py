from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Tour, TourPicture
from .serializers import TourSerializer, TourPictureSerializer
from .permissions import IsTheGuideOwnerOrReadOnly

class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsTheGuideOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(guide=self.request.user.guide)


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
