from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import UserProfile



@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_delete, sender=User)
def delete_profile_on_user_delete(sender, instance, **kwargs):
    UserProfile.objects.filter(user=instance).delete()


@receiver(pre_save, sender=UserProfile)
def update_employee_id(sender, instance, **kwargs):
    if instance.pk:                      # only on updates / creates with PK
        slug = (instance.work_location or "NA").upper().replace(" ", "")
        new_id = f"KMDV-{slug}-{instance.pk}"
        if instance.employee_id != new_id:
            instance.employee_id = new_id