from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from knowhub import settings


@shared_task
def invite(data):
    send_mail(
        data['cult_name'] + ' announcement: ' + data['event_title'] + ' event',
        render_to_string(
            'main/invite_email.txt',
            {'data': data},
        ),
        settings.DEFAULT_FROM_EMAIL,
        [data['member_email']],
    )
