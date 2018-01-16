from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class AdminUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    phone_number = forms.CharField(max_length=32)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'username', 'email', 'groups')


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)
