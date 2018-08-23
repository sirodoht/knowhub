from django import forms
from django.contrib.auth.models import User

from . import models


class EmailForm(forms.Form):
    email = forms.EmailField(label="Your email address")


class CompanyForm(forms.ModelForm):
    class Meta:
        model = models.Company
        fields = ["name"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Your email")

    class Meta:
        model = models.Profile
        fields = ["name", "role", "slack"]


class InviteSetupForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ["name", "role", "slack"]


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = models.Company
        fields = ["name"]


class ResourceForm(forms.ModelForm):
    tags = forms.CharField(label="Tags", strip=True, max_length=300, required=False)

    class Meta:
        model = models.Resource
        fields = ["title", "body"]


class DeleteResourceForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = []


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = models.Subscriber
        fields = ["email", "ip"]


class ExplorerForm(forms.ModelForm):
    class Meta:
        model = models.Explorer
        fields = ["email"]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ["title", "body"]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ["body"]
