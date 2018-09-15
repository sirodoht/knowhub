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
    path("invite/", views.invite, name="invite"),
    path("invited/", views.invite_verify, name="invite_verify"),
    path("setup/", views.invite_setup, name="invite_setup"),
    path("invitation/", views.invite_open_verify, name="invite_open_verify"),
    path("invitation/refresh/", views.invite_open_refresh, name="invite_open_refresh"),
    path("googlef6b7b346eca71466.html", views.google_verify, name="google_verify"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("blog/", views.blog, name="blog"),
    path("blog/subscribe/", views.blog_subscribe, name="blog_subscribe"),
    path("blog/<slug:post_slug>/", views.blog_post, name="blog_post"),
    path("billing/", views.billing_setup, name="billing_setup"),
    path("billing/customer/", views.billing_customer, name="billing_customer"),
    path("settings/", views.settings_user, name="settings_user"),
    path("settings/billing/", views.billing_settings, name="billing_settings"),
    path("settings/delete/", views.account_delete, name="account_delete"),
    path("settings/company/", views.settings_company, name="settings_company"),
    path("settings/company/logo/", views.company_logo, name="company_logo"),
    path("settings/photo/", views.profile_photo, name="profile_photo"),
    path("users/deactivate/", views.users_deactivate, name="users_deactivate"),
    path("users/activate/", views.users_activate, name="users_activate"),
    path("users/adminify/", views.users_adminify, name="users_adminify"),
    path("users/deadminify/", views.users_deadminify, name="users_deadminify"),
    path("profile/<uuid:route>/", views.profile, name="profile"),
    path("people/", views.people, name="people"),
    path("announce/", views.announce, name="announce"),
    path("documents/", views.resources, name="resources"),
    path("documents/pins/", views.resources_pins, name="resources_pins"),
    path("documents/new/", views.resources_create, name="resources_create"),
    path(
        "documents/<slug:resource_slug>/", views.resources_view, name="resources_view"
    ),
    path(
        "documents/<slug:resource_slug>/edit/",
        views.resources_edit,
        name="resources_edit",
    ),
    path(
        "documents/<slug:resource_slug>/delete/",
        views.resources_delete,
        name="resources_delete",
    ),
    path("questions/", views.questions, name="questions"),
    path("questions/ask", views.questions_create, name="questions_create"),
    path(
        "questions/<slug:question_slug>/", views.questions_view, name="questions_view"
    ),
    path(
        "questions/<slug:question_slug>/edit/",
        views.questions_edit,
        name="questions_edit",
    ),
    path(
        "questions/<slug:question_slug>/delete/",
        views.questions_delete,
        name="questions_delete",
    ),
    path(
        "questions/<slug:question_slug>/edit/<int:answer_id>",
        views.questions_edit_answer,
        name="questions_edit_answer",
    ),
    path(
        "questions/<slug:question_slug>/delete/<int:answer_id>",
        views.questions_delete_answer,
        name="questions_delete_answer",
    ),
]
