from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

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
            # Uncomment to change groups widget to a dropdown.
            # NOTE/TODO: If uncommented, the form needs work to validate single groups
            # User should currently only be attached to one group (though its a m2m)
            # self.fields['groups'].widget = forms.Select()
            # self.fields['groups'].queryset = Group.objects.all()
            # self.fields['groups'].initial = self.instance.groups.first()

            if not self.user.is_superuser and self.user.is_staff:
                self.fields['groups'].queryset = Group.objects.filter(
                    pk__in=self.user.groups.all().values_list('pk', flat=True)
                )

    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class AdminUserProfileForm(UserInjectionMixin, forms.ModelForm):
    class Meta:
        model = TelmedxProfile
        fields = ('first_name', 'last_name', 'phone')


class AdminGroupForm(UserInjectionMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)


class AdminGroupProfileForm(UserInjectionMixin, forms.ModelForm):
    class Meta:
        model = TelmedxGroupProfile
        fields = ('contact_name', 'contact_email', 'contact_phone')


class LogoWidget(forms.FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and hasattr(value, 'url'):
            output.append("""
                <div class="logo-display">
                Currently: 
                <a target="_blank" href="{url}">
                    <img src={url} style="height:30px" />
                </a>
                </div>
            """.format(url=value.url))

        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output))


class GroupAndProfileForm(UserInjectionMixin, forms.Form):
    name = forms.CharField(max_length=80, label='Group Name')
    contact_name = forms.CharField(label='Contact Name')
    contact_email = forms.EmailField(label='Contact Email')
    contact_phone = forms.CharField(label='Contact Phone', max_length=64)
    logo = forms.ImageField(label='Upload Logo', widget=LogoWidget, required=False)


class UserAndProfileForm(UserInjectionMixin, forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()
    phone = forms.CharField()
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    is_group_admin = forms.BooleanField(label='Is group admin', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only superusers can set if a user is a group admin?
        # Only show group admin checkbox when creating a user
        # Check if initial dict is populated.
        if (self.user and not self.user.is_superuser) or \
            (len(self.initial)):
            del self.fields['is_group_admin']

