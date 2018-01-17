from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class AdminUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    phone = forms.CharField(max_length=32)

    def get_initial_for_field(self, field, field_name):
        value = super().get_initial_for_field(field, field_name)

        if not value:
            initial = getattr(self.instance.profile, field_name)
            if initial:
                value = initial

        return value

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'username', 'email', 'groups')

    def save(self, commit=True, **kwargs):
        data = self.data
        profile = self.instance.profile

        profile.phone = data.get('phone')
        profile.first_name = data.get('first_name')
        profile.last_name = data.get('last_name')

        return super().save(commit)


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)
