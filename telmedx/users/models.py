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
    group = models.OneToOneField(Group)
    contact = models.EmailField()


class TelmedxUserManager(UserManager):

    def create_group_admin(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('user_type', USER_GROUP_ADMIN)
        return self._create_user(username, email, password, **extra_fields)


class TelmedxProfile(models.Model):
    user = models.OneToOneField('TelmedxUser', related_name='profile')
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
