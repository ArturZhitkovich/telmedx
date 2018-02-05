from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import TelmedxUserSerializer

User = get_user_model()

__all__ = (
    'UserUpdateAPIView',
)


class UserUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = TelmedxUserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to edit themselves
        if not self.request.user:
            raise PermissionDenied('Permission denied')
        return self.queryset
