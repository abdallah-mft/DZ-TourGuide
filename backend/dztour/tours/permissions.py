from rest_framework import permissions

class IsTheGuideOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return (
            user.is_authenticated and 
            user.role == 'guide' and 
            hasattr(user, 'profile') and 
            user.profile.is_verified == True
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.guide.user == request.user