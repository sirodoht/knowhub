import stripe
from django.apps import AppConfig

from knowhub import settings


class MainConfig(AppConfig):
    name = "main"

    def ready(self):
        stripe.api_key = settings.STRIPE_SECRET
