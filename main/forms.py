from django import forms
from django.contrib.auth.models import User


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address')
