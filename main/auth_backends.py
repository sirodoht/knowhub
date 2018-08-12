import base64
import json

from django.contrib.auth import get_user_model
from django.core.signing import BadSignature, Signer

from .helpers import generate_username

# from knowhub import settings
# import time


class EmailTokenBackend:
    """
    Code stolen from https://github.com/skorokithakis/django-tokenauth/tree/v0.1.0
    """

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, token=None):
        try:
            data = Signer().unsign(token)
        except BadSignature:
            return

        data = json.loads(base64.b64decode(data).decode("utf8"))
        # if data["t"] < time.time() - settings.AUTH_TOKEN_DURATION:
        #     return

        User = get_user_model()

        user, created = User.objects.get_or_create(email=data["e"])
        if created:
            user.username = generate_username(data["e"])
            user.save()

        return user
