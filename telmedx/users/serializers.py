from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

User = get_user_model()


class TelmedxUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    phone = serializers.CharField(source='profile.phone')
    email = serializers.EmailField(required=True)
    group = serializers.CharField(source='groups.first.name', required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'group',
            'password',
        )

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.email = validated_data.get('email')
        instance.save()
        profile_data = validated_data.get('profile')
        instance.profile.first_name = profile_data.get('first_name')
        instance.profile.last_name = profile_data.get('last_name')
        instance.profile.phone = profile_data.get('phone')
        instance.save()

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'password' in ret:
            del ret['password']
        return ret


class TelmedxGroupSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='profile.contact_name')
    contact_email = serializers.EmailField(source='profile.contact_email')
    contact_phone = serializers.CharField(source='profile.contact_phone')

    class Meta:
        model = Group
        fields = ('id', 'name', 'contact_email', 'contact_name', 'contact_phone')
