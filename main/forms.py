from django import forms
from django.contrib.auth.models import User

from .models import Company, Resource


class EmailForm(forms.Form):
    email = forms.EmailField(label="Your email address")


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]


class UserSettingsForm(forms.ModelForm):
    slack = forms.CharField(label="Your Slack username")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name"]


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "body"]
