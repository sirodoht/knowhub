from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from knowhub import settings


@shared_task
def invite_task(data):
    send_mail(
        "Invitation for " + data["company_name"] + " at KnowHub.app",
        render_to_string("main/invite_email.txt", {"data": data}),
        settings.DEFAULT_FROM_EMAIL,
        [data["email"]],
    )
