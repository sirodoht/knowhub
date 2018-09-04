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


def info_get(stripe_id):
    customer = stripe.Customer.retrieve(stripe_id)
    info = {}
    info["brand"] = customer["sources"]["data"][0]["brand"]
    info["exp_month"] = customer["sources"]["data"][0]["exp_month"]
    info["exp_year"] = customer["sources"]["data"][0]["exp_year"]
    info["last4"] = customer["sources"]["data"][0]["last4"]
    info["quantity"] = customer["subscriptions"]["data"][0]["quantity"]
    info["cost"] = 2 * info["quantity"]
    info["trial"] = False
    if customer["subscriptions"]["data"][0]["status"] == "trialing":
        info["trial"] = True
    return info


def card_change(stripe_id, new_token):
    if stripe_id is None:
        return
    customer = stripe.Customer.retrieve(stripe_id)
    customer.source = new_token
    return customer.save()
