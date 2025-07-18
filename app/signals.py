from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_delete, sender=User)
def delete_profile_on_user_delete(sender, instance, **kwargs):
    UserProfile.objects.filter(user=instance).delete()