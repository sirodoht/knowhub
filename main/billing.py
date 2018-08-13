import stripe

from knowhub import settings

from . import models


def customer_create(user_email, token):
    return stripe.Customer.create(email=user_email, source=token)


def subscription_create(customer_id):
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"plan": settings.STRIPE_PLAN}],
        trial_period_days=30,
    )


def subscription_upgrade(user, added_quantity=1):
    if user.profile.stripe_id:
        stripe_id = user.profile.stripe_id
    else:
        stripe_id = (
            models.Profile.objects.filter(
                company=user.profile.company, stripe_id__isnull=False
            )
            .first()
            .stripe_id
        )
    customer = stripe.Customer.retrieve(stripe_id)
    quantity = customer["subscriptions"]["data"][0]["items"]["data"][0]["quantity"]
    subscription = customer["subscriptions"]["data"][0]
    new_quantity = quantity + added_quantity
    subscription.quantity = new_quantity
    return subscription.save()
