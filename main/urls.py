from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = "KnowHub administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("entrance/", views.login, name="register"),
    path("entrance/", views.login, name="login"),
    path("auth/", views.token_post, name="auth"),
    path("logout/", views.logout, name="logout"),
    path("init/", views.company_new, name="company_new"),
    path("invitation/", views.invite_verify, name="invite_verify"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:post_slug>/", views.blog_post, name="blog_post"),
    path("<slug:route>/people/", views.people, name="people"),
    path("<slug:route>/resources/", views.resources, name="resources"),
    path("<slug:route>/questions/", views.questions, name="questions"),
    path("<slug:route>/billing/", views.billing_setup, name="billing_setup"),
    path(
        "<slug:route>/billing/customer/",
        views.billing_customer,
        name="billing_customer",
    ),
    path("<slug:route>/invite/", views.invite, name="invite"),
    path("<slug:route>/settings/", views.settings_user, name="settings_user"),
    path(
        "<slug:route>/settings/company/",
        views.settings_company,
        name="settings_company",
    ),
    path(
        "<slug:route>/settings/company/logo/", views.company_logo, name="company_logo"
    ),
    path("<slug:route>/settings/photo/", views.profile_photo, name="profile_photo"),
    path("<slug:route>/profile/<slug:username>/", views.profile, name="profile"),
]
