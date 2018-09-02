import base64
import datetime
import json
import time

import pytz
import shortuuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, Signer
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify

from knowhub import settings

from .models import Analytic, Company


def email_login_link(request, email):
    current_site = get_current_site(request)

    # Create signed structure containing the time and email address.
    email = email.lower().strip()
    data = {"t": int(time.time()), "e": email}
    data = json.dumps(data).encode("utf8")
    data = Signer().sign(base64.b64encode(data).decode("utf8"))

    send_mail(
        "Sign in to KnowHub",
        render_to_string(
            "main/token_auth_email.txt",
            {"current_site": current_site, "data": data},
            request=request,
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


def generate_username(email):
    username = email.split("@")[0].replace("+", "-")
    username = slugify(username)

    # check if exists
    if User.objects.filter(username=username).count():
        uuid = shortuuid.ShortUUID(
            "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
        ).random(length=12)
        username += uuid

    return username


def get_invite_data(request, email, company):
    email = email.lower().strip()
    info = {"c": company.route, "e": email}
    info = json.dumps(info).encode("utf8")
    signed_info = Signer().sign(base64.b64encode(info).decode("utf8"))

    domain = get_current_site(request).domain
    invitation_url = domain + reverse("main:invite_verify") + "?d=" + signed_info
    if "localhost" in domain or "127.0.0.1" in domain:
        invitation_url = "http://" + invitation_url
    else:
        invitation_url = "https://" + invitation_url

    data = {
        "email": email,
        "inviter_name": request.user.profile.name,
        "inviter_email": request.user.email,
        "company_name": company.name,
        "invitation_url": invitation_url,
        "signed_info": signed_info,
    }

    return data


def verify_invite_data(token=None):
    try:
        data = Signer().unsign(token)
    except BadSignature:
        return

    data = json.loads(base64.b64decode(data).decode("utf8"))

    User = get_user_model()
    company = Company.objects.get(route=data["c"])

    user, created = User.objects.get_or_create(email=data["e"])
    if created:
        user.username = generate_username(data["e"])
        user.profile.company = company
        user.save()

    return user


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def log_analytic(request):
    new_analytic = Analytic(
        querystring=request.GET.urlencode(),
        ip=get_client_ip(request),
        path=request.path,
    )
    if request.user.is_authenticated:
        new_analytic.user = User.objects.get(id=request.user.id)
    new_analytic.save()


def get_timezones_form():
    timezones = []
    timezones_name = pytz.common_timezones
    for name in timezones_name:
        if name == "GMT":
            continue

        offset = datetime.datetime.now(pytz.timezone(name)).strftime("%z")
        offset_pretty = "UTC" + offset[:3] + ":" + offset[3:]

        name_pretty = name
        if "/" in name:
            name_pretty = name.replace("_", " ")
        timezones.append({"code": name, "name": name_pretty, "offset": offset_pretty})

    timezones_sorted = sorted(timezones, key=lambda k: k["offset"])
    timezones_utc = timezones_sorted[:19]
    timezones_plus = timezones_sorted[19:263]
    timezones_minus = reversed(timezones_sorted[263:])
    timezones_synthesized = [*timezones_minus, *timezones_utc, *timezones_plus]

    return timezones_synthesized


def get_open_invite(request, refresh=False):
    company = request.user.profile.company

    if not company.invite_data or refresh:
        data = {"t": int(time.time()), "c": company.route}

        data = json.dumps(data).encode("utf8")
        data = Signer().sign(base64.b64encode(data).decode("utf8"))

        company.invite_data = data
        company.save()

    domain = get_current_site(request).domain
    open_invite_url = (
        domain + reverse("main:invite_open_verify") + "?d=" + company.invite_data
    )
    if "localhost" in domain or "127.0.0.1" in domain:
        open_invite_url = "http://" + open_invite_url
    else:
        open_invite_url = "https://" + open_invite_url

    return open_invite_url


def verify_open_invite_data(token=None):
    try:
        data = Signer().unsign(token)
    except BadSignature:
        return

    data = json.loads(base64.b64decode(data).decode("utf8"))

    # check if there is company info in invite data
    if not data["c"]:
        return

    # check if company info is vaid
    company_route = data["c"]
    if not Company.objects.filter(route=company_route).exists():
        return

    # check if company info hasn't been reset
    company = Company.objects.get(route=company_route)
    if company.invite_data != token:
        return

    return company_route
