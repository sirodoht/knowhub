import base64
import json
import time

import shortuuid
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import Signer
from django.template.loader import render_to_string

from knowhub import settings


def email_login_link(request, email):
    current_site = get_current_site(request)

    # Create signed structure containing the time and email address.
    email = email.lower().strip()
    data = {"t": int(time.time()), "e": email}
    data = json.dumps(data).encode("utf8")
    data = Signer().sign(base64.b64encode(data).decode("utf8"))

    send_mail(
        "Sign in to KnowHub.app",
        render_to_string(
            "main/token_auth_email.txt",
            {"current_site": current_site, "data": data},
            request=request,
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


def generate_username(email):
    username = email.split("@")[0]

    # check if exists
    if User.objects.filter(username=username).count():
        uuid = shortuuid.ShortUUID(
            "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
        ).random(length=12)
        username += uuid

    return username


def email_invite_link(request, email, company):
    current_site = get_current_site(request)

    email = email.lower().strip()
    data = {"t": int(time.time()), "e": email}
    data = json.dumps(data).encode("utf8")
    data = Signer().sign(base64.b64encode(data).decode("utf8"))

    send_mail(
        "You have been invited to KnowHub.app",
        render_to_string(
            "main/invite_email.txt",
            {"current_site": current_site, "company": company, "data": data},
            request=request,
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


def verify_invite_data(token=None):
    try:
        data = Signer().unsign(token)
    except BadSignature:
        return False

    data = json.loads(base64.b64decode(data).decode("utf8"))

    User = get_user_model()

    user, created = User.objects.get_or_create(email=data["e"])
    if created:
        user.username = generate_username(data["e"])
        user.save()

    return user
