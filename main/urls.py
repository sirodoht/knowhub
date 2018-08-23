from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = "KnowHub administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("subscribe/thanks/", views.subscribe_thanks, name="subscribe_thanks"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("join/", views.register, name="register"),
    path("signin/", views.login, name="login"),
    path("auth/", views.token_post, name="auth"),
    path("logout/", views.logout, name="logout"),
    path("init/", views.company_new, name="company_new"),
    path("invitation/", views.invite_verify, name="invite_verify"),
    path("googlef6b7b346eca71466.html", views.google_verify, name="google_verify"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("blog/", views.blog, name="blog"),
    path("blog/subscribe/", views.blog_subscribe, name="blog_subscribe"),
    path("blog/<slug:post_slug>/", views.blog_post, name="blog_post"),
    path("<slug:route>/", views.company, name="company"),
    path("<slug:route>/setup/", views.invite_setup, name="invite_setup"),
    path("<slug:route>/people/", views.people, name="people"),
    path("<slug:route>/resources/", views.resources, name="resources"),
    path(
        "<slug:route>/resources/new/", views.resources_create, name="resources_create"
    ),
    path(
        "<slug:route>/resources/<slug:resource_slug>/",
        views.resources_view,
        name="resources_view",
    ),
    path(
        "<slug:route>/resources/<slug:resource_slug>/edit/",
        views.resources_edit,
        name="resources_edit",
    ),
    path(
        "<slug:route>/resources/<slug:resource_slug>/delete/",
        views.resources_delete,
        name="resources_delete",
    ),
    path("<slug:route>/questions/", views.questions, name="questions"),
    path("<slug:route>/questions/ask", views.questions_create, name="questions_create"),
    path(
        "<slug:route>/questions/<slug:question_slug>/",
        views.questions_view,
        name="questions_view",
    ),
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
