import uuid

from django.contrib.auth.models import AbstractUser, UserManager, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

USER_GLOBAL_ADMIN = 1
USER_GROUP_ADMIN = 2
USER_REGULAR_USER = 3
USER_TYPES_CHOICES = (
    (USER_GLOBAL_ADMIN, 'Global Admin'),
    (USER_GROUP_ADMIN, 'Group Admin'),
    (USER_REGULAR_USER, 'User'),
)


class TelmedxGroupProfile(models.Model):
    group = models.OneToOneField(Group, related_name='profile', on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=128)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to='group_logos', blank=True, null=True)

    def get_users(self, user_type):
        """
        :param user: User which is requesting the user set.
                     Used for checking permissions on the queryset.
        :type user: TelmedxUser
        :return:
        """
        qs = self.group.user_set.filter(is_superuser=False)

        if user_type == 'admin':
            qs = qs.filter(is_staff=True)
        elif user_type == 'mobile':
            qs = qs.filter(is_staff=False)
        else:
            raise ValueError('`user_type` does not exist')

        return qs

    @property
    def mobile_users(self):
        return self.get_users('mobile')

    @property
    def admin_users(self):
        return self.get_users('admin')


class TelmedxUserManager(UserManager):

    def create_group_admin(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('user_type', USER_GROUP_ADMIN)
        return self._create_user(username, email, password, **extra_fields)


class TelmedxProfile(models.Model):
    user = models.OneToOneField('TelmedxUser', related_name='profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=120)
    user_type = models.SmallIntegerField(choices=USER_TYPES_CHOICES,
                                         default=USER_REGULAR_USER)

    def __str__(self):
        if self.first_name and self.last_name:
            ret = 'Profile: {}, {}'.format(
                self.last_name, self.first_name
            )
        else:
            ret = 'Profile for user: {}'.format(self.user.pk)
        return ret


class TelmedxUser(AbstractUser):
    objects = TelmedxUserManager()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    @property
    def date_created(self):
        return self.date_joined

    @property
    def first_name(self):
        if self.profile:
            return self.profile.first_name

    @property
    def last_name(self):
        if self.profile:
            return self.profile.last_name


# Uncomment if we want to have email == username
# @receiver(pre_save, sender=TelmedxUser)
# def populate_username(sender, instance, **kwargs):
#     instance.username = instance.email
#     return instance


@receiver(post_save, sender=TelmedxUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        TelmedxProfile.objects.create(user=instance)


@receiver(post_save, sender=TelmedxUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Group)
def create_group_profile(sender, instance, created, **kwargs):
    if created:
        TelmedxGroupProfile.objects.create(group=instance)
