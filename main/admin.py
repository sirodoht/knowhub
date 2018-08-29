from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models


# User
class KnowhubAdmin(UserAdmin):
    list_display = ("username", "email", "date_joined", "last_login", "id")


admin.site.unregister(User)
admin.site.register(User, KnowhubAdmin)


# Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "stripe_id", "id")


admin.site.register(models.Profile, ProfileAdmin)


# Company
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "id")


admin.site.register(models.Company, CompanyAdmin)


# Resource
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "company")


admin.site.register(models.Resource, ResourceAdmin)


# Post
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "date")


admin.site.register(models.Post, PostAdmin)


# Subscriber
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "ip", "created_at")


admin.site.register(models.Subscriber, SubscriberAdmin)


# Explorer
class ExplorerAdmin(admin.ModelAdmin):
    list_display = ("email", "ip", "created_at")


admin.site.register(models.Explorer, ExplorerAdmin)


# Analytic
class AnalyticAdmin(admin.ModelAdmin):
    list_display = ("ip", "user", "created_at", "path", "querystring")


admin.site.register(models.Analytic, AnalyticAdmin)


# Question
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "author", "company", "created_at", "updated_at")


admin.site.register(models.Question, QuestionAdmin)


# Answer
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("body", "question", "created_at", "updated_at")


admin.site.register(models.Answer, AnswerAdmin)


# Tag
class TagAdmin(admin.ModelAdmin):
    list_display = ("text",)


admin.site.register(models.Tag, TagAdmin)


# TagResource
class TagResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "resource")


admin.site.register(models.TagResource, TagResourceAdmin)


# CompanyTag
class CompanyTagAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "company")


admin.site.register(models.CompanyTag, CompanyTagAdmin)
