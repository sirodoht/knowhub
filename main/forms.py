from django import forms
from django.contrib.auth.models import User

from .models import Company


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


class SettingsForm(forms.ModelForm):
    slack = forms.CharField(label="Your Slack username")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
