from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import TelmedxUserSerializer

User = get_user_model()

__all__ = (
    'UserUpdateAPIView',
    'UserProfileAPIView',
)


class UserProfileAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TelmedxUserSerializer

    def get_object(self):
        # Just return the current user
        queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(queryset, pk=self.request.user.pk)


class UserUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = TelmedxUserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        # User should only be able to edit themselves
        if not self.request.user.uuid == self.get_object().uuid:
            raise PermissionDenied('Permission denied')
        return self.queryset
