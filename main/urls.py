from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = "KnowHub administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("entrance/", views.login, name="login"),
    path("auth/", views.token_post, name="auth"),
    path("logout/", views.logout, name="logout"),
    path("init/", views.company_new, name="company_new"),
    path("billing/", views.billing_setup, name="billing_setup"),
    path("billing/customer/", views.billing_customer, name="billing_customer"),
    path("invite/", views.invite, name="invite"),
    path("profile/", views.profile, name="profile"),
]
