import stripe

from knowhub import settings


def customer_create(user_email, token):
    return stripe.Customer.create(email=user_email, source=token)


def subscription_create(customer_id):
    return stripe.Subscription.create(
        customer=customer_id, items=[{"plan": settings.STRIPE_PLAN}]
    )
