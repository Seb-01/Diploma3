from rest_framework.permissions import IsAdminUser

class MyIsAdminUser(IsAdminUser):
    """

    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin and request.user.is_superuser)