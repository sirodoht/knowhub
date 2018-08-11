import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=300)
    route = models.CharField(max_length=50, unique=True, null=True, default=None)
    logo = models.ImageField(default="/static/images/logo.svg")

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(default="/static/images/person.svg")
    is_admin = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=300, blank=True, null=True)
    slack = models.CharField(max_length=300, blank=True, null=True)
    interests = models.TextField(max_length=600, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    work_start = models.TimeField(blank=True, null=True)
    work_end = models.TimeField(blank=True, null=True)
    agenda = models.TextField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Resource(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300)
    body = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def as_markdown(self):
        return markdown.markdown(self.body)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300)
    body = models.TextField()
    date = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def as_markdown(self):
        return markdown.markdown(self.body)

    def __str__(self):
        return self.title


class Subscriber(models.Model):
    email = models.EmailField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class Analytic(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=400, null=True, blank=True)
    querystring = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return self.ip


class Explorer(models.Model):
    email = models.EmailField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
