from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import TelmedxProfile

User = get_user_model()


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class AdminUserProfileForm(forms.ModelForm):
    class Meta:
        model = TelmedxProfile
        fields = ('first_name', 'last_name', 'phone')


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)
