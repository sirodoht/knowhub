import stripe

from knowhub import settings


def customer_create(user_email, token):
    return stripe.Customer.create(email=user_email, source=token)
