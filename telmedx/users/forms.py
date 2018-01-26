from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import TelmedxProfile, TelmedxGroupProfile

User = get_user_model()


class UserInjectionMixin:
    user = None

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class AdminUserForm(UserInjectionMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user:
            if not self.user.is_superuser and self.user.is_staff:
                self.fields['groups'].queryset = Group.objects.filter(
                    pk__in=self.user.groups.all().values_list('pk', flat=True)
                )

    # def clean_groups(self, *args, **kwargs):
        

    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class AdminUserProfileForm(UserInjectionMixin, forms.ModelForm):
    class Meta:
        model = TelmedxProfile
        fields = ('first_name', 'last_name', 'phone')


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)


class AdminGroupProfileForm(forms.ModelForm):
    class Meta:
        model = TelmedxGroupProfile
        fields = ('contact',)
