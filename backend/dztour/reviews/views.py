from rest_framework import permissions, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .models import Review
from tours.models import Tour
from .serializers import ReviewSerializer
from .permissions import IsReviewAuthorOrReadOnly

class CreateReview(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

class DestroyUpdateReview(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    lookup_field = 'id'
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewAuthorOrReadOnly]

@api_view(['GET'])
def get_tour_reviews(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    reviews = Review.objects.filter(booking__tour=tour)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def guide_get_my_reviews(request):
    user = request.user
    if user.role != 'guide':
        return Response({'error': 'Tourists can not get reviews'}, status=status.HTTP_403_FORBIDDEN)

    reviews = Review.objects.filter(guide=user)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)