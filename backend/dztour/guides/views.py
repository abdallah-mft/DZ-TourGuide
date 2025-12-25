from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from .models import GuideProfile, Language, Wilaya, Commune, Certifications
from .serializers import (
    GuideProfileSerializer,
    GuideProfileCreateUpdateSerializer,
    LanguageSerializer,
    WilayaSerializer,
    CommuneSerializer,
    CertificationSerializer
)


class IsGuideUser(permissions.BasePermission):
    """Only allow users with role='guide' to create/update profiles."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'guide'


class IsProfileOwner(permissions.BasePermission):
    """Only allow owners to edit their profile."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class GuideProfileViewSet(viewsets.ModelViewSet):
    queryset = GuideProfile.objects.select_related('user').prefetch_related(
        'languages_spoken', 'wilaya_covered', 'commune_covered', 'certifications'
    )
    permission_classes = [IsGuideUser, IsProfileOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'me']:
            return GuideProfileCreateUpdateSerializer
        return GuideProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'patch', 'delete'], permission_classes=[permissions.IsAuthenticated, IsGuideUser])
    def me(self, request):
        """Get, update, or delete current user's guide profile."""
        try:
            profile = GuideProfile.objects.select_related('user').prefetch_related(
                'languages_spoken', 'wilaya_covered', 'commune_covered', 'certifications'
            ).get(user=request.user)
        except GuideProfile.DoesNotExist:
            return Response(
                {"detail": "Guide profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = GuideProfileSerializer(profile)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = GuideProfileCreateUpdateSerializer(
                profile, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(GuideProfileSerializer(profile).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Certifications.objects.filter(guide_profile__user=self.request.user)

    def perform_create(self, serializer):
        profile = GuideProfile.objects.get(user=self.request.user)
        serializer.save(guide_profile=profile)


class LanguageListView(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


class WilayaListView(generics.ListAPIView):
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializer
    permission_classes = [permissions.AllowAny]


class CommuneListView(generics.ListAPIView):
    serializer_class = CommuneSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Commune.objects.select_related('wilaya')
        wilaya_code = self.request.query_params.get('wilaya')
        if wilaya_code:
            queryset = queryset.filter(wilaya__code=wilaya_code)
        return queryset
