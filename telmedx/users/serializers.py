from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

User = get_user_model()


class TelmedxUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    phone = serializers.CharField(source='profile.phone')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone')


class TelmedxGroupSerializer(serializers.ModelSerializer):
    contact = serializers.EmailField(source='profile.contact')

    class Meta:
        model = Group
        fields = ('id', 'name', 'contact')
