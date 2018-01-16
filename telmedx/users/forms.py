from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)
