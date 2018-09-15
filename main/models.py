import uuid

import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=300)
    route = models.CharField(max_length=50, unique=True, null=True, default=None)
    logo = models.ImageField(
        default="/static/images/company-profile.png", max_length=300
    )
    invite_data = models.CharField(blank=True, null=True, max_length=700)

    def __str__(self):
        return self.name


class Profile(models.Model):
    route = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(default="/static/images/profile.png", max_length=300)
    is_admin = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=300, blank=True, null=True)
    slack = models.CharField(max_length=300, blank=True, null=True)
    interests = models.TextField(max_length=600, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    time_zone = models.CharField(max_length=300, default="UTC")
    work_start = models.TimeField(blank=True, null=True)
    work_end = models.TimeField(blank=True, null=True)
    agenda = models.TextField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.user.email

    class Meta:
        ordering = ["name"]


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
    tags = models.ManyToManyField("Tag", through="CompanyTag")

    @property
    def tags(self):
        return ",".join([tag.text for tag in self.tag_set.all()])

    @property
    def as_markdown(self):
        return markdown.markdown(
            self.body,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ],
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300)
    body = models.TextField()
    date = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def as_markdown(self):
        return markdown.markdown(
            self.body,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ],
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]


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


class Question(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300)
    body = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def as_markdown(self):
        return markdown.markdown(
            self.body,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ],
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated_at"]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def as_markdown(self):
        return markdown.markdown(
            self.body,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ],
        )

    def __str__(self):
        return self.body[:100]

    class Meta:
        ordering = ["created_at"]


class Tag(models.Model):
    resources = models.ManyToManyField(Resource, through="TagResource")
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text


class TagResource(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.text + "-" + self.resource.title


class CompanyTag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.company.name + "-" + self.tag.text
