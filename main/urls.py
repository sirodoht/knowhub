from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = 'KnowHub administration'
app_name = 'main'

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /entrance/
    path('entrance/', views.login, name='login'),

    # /auth/
    path('auth/', views.token_post, name='auth'),

    # /logout/
    path('logout/', views.logout, name='logout'),

    # /init/
    path('init/', views.company_new, name='company_new'),
]
