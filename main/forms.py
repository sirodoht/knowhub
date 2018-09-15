from django import forms
from django.contrib.auth.models import User

from . import models


class EmailForm(forms.Form):
    email = forms.EmailField(label="Your email address")


class CompanyForm(forms.ModelForm):
    profile_name = forms.CharField(label="Your name", strip=True, max_length=300)

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
        fields = [
            "name",
            "role",
            "slack",
            "time_zone",
            "location",
            "work_start",
            "work_end",
        ]


class InviteSetupForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ["name", "role"]


class InviteOpenSetupForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    invite_token = forms.CharField(max_length=300)

    class Meta:
        model = models.Profile
        fields = ["name", "role"]


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


class DeleteQuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
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


class DeleteAnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = []


class AnnounceForm(forms.Form):
    subject = forms.CharField(label="Subject", strip=True, max_length=300)
    body = forms.CharField(label="Body", widget=forms.Textarea)
