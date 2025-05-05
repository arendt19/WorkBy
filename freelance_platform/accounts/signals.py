from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, FreelancerProfile, ClientProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль при создании пользователя"""
    if created:
        if instance.user_type == 'freelancer':
            FreelancerProfile.objects.create(user=instance)
        else:
            ClientProfile.objects.create(user=instance) 