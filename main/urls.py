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
    path("invitation/", views.invite_verify, name="invite_verify"),
    path("<slug:route>/", views.company, name="company"),
    path("<slug:route>/billing/", views.billing_setup, name="billing_setup"),
    path(
        "<slug:route>/billing/customer/",
        views.billing_customer,
        name="billing_customer",
    ),
    path("<slug:route>/invite/", views.invite, name="invite"),
    path("<slug:route>/settings/", views.settings, name="settings"),
    path("<slug:route>/profile/photo/", views.profile_photo, name="profile_photo"),
    path("<slug:route>/profile/<slug:username>/", views.profile, name="profile"),
]
