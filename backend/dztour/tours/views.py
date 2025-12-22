from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Tour
from .serializers import TourSerializer
from .permissions import IsTheGuideOwnerOrReadOnly

class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [IsTheGuideOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(guide=self.request.user.guide)
