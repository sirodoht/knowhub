from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models


# User
class KnowhubAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'id',)


admin.site.unregister(User)
admin.site.register(User, KnowhubAdmin)


# Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'stripe_id', 'id',)


admin.site.register(models.Profile, ProfileAdmin)


# Company
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)


admin.site.register(models.Company, CompanyAdmin)
