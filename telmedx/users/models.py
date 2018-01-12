from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class TelmedxProfile(models.Model):
    user = models.OneToOneField('TelmedxUser', related_name='profile')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=120)


class TelmedxUser(AbstractUser):

    @property
    def date_created(self):
        return self.date_joined


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
