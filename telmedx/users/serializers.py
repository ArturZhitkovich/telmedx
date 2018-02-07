from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

User = get_user_model()


class TelmedxUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    phone = serializers.CharField(source='profile.phone')
    email = serializers.EmailField(required=True)
    group = serializers.CharField(source='groups.first.name')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'group'
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.save()
        profile_data = validated_data.get('profile')
        instance.profile.first_name = profile_data.get('first_name')
        instance.profile.last_name = profile_data.get('last_name')
        instance.profile.phone = profile_data.get('phone')
        instance.save()

        return instance


class TelmedxGroupSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='profile.contact_name')
    contact_email = serializers.EmailField(source='profile.contact_email')
    contact_phone = serializers.CharField(source='profile.contact_phone')

    class Meta:
        model = Group
        fields = ('id', 'name', 'contact_email', 'contact_name', 'contact_phone')
