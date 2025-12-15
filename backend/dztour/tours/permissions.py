from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerTourOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.action in ['list', 'retrieve']:
            return True

        return obj.guide.user == request.user