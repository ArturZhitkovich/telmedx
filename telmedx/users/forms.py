from django import forms
from django.contrib.auth.models import User, Group


class AdminUserForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        strip=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        # TODO: Convert to TelmedxUser
        model = User
        fields = (
            'username', 'email', 'groups',
        )



class AdminGroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=80,
        strip=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Group
        fields = ('name',)
