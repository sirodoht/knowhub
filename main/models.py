from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Company(models.Model):
    name = models.CharField(max_length=300)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(default='images/profile.svg')
    is_admin = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=300, blank=True, null=True)
    slack = models.TextField(max_length=300, blank=True, null=True)
    interests = models.TextField(max_length=600, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    work_start = models.TimeField(blank=True, null=True)
    work_end = models.TimeField(blank=True, null=True)
    agenda = models.TextField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
