import json

import shortuuid
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from knowhub import settings

from . import billing
from .forms import (
    CompanyForm,
    CompanySettingsForm,
    EmailForm,
    UserForm,
    UserSettingsForm,
)
from .helpers import email_login_link, get_invite_data, verify_invite_data
from .models import Company
from .tasks import invite_task


def index(request):
    if request.user.is_authenticated:
        if not request.user.profile.company:
            return redirect("main:company_new")
        if request.user.profile.is_admin and not request.user.profile.stripe_id:
            return redirect("main:billing_setup")
        return redirect("main:people", request.user.profile.company.route)
    else:
        return render(request, "main/marketing.html")


def people(request, route):
    if request.user.is_authenticated:
        company = Company.objects.get(route=route)
        people = User.objects.all().filter(
            profile__company=request.user.profile.company
        )
        return render(
            request, "main/people.html", {"company": company, "people": people}
        )
    else:
        return redirect(request, "main:index")


@require_safe
def login(request):
    if request.user.is_authenticated:
        return redirect("main:index")
    return render(request, "main/login.html", {"next": request.GET.get("next")})


@require_http_methods(["HEAD", "GET", "POST"])
def token_post(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already signed in.")
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get("d"):
        # The user has clicked a login link.
        user = authenticate(token=request.GET["d"])
        if user is not None:
            dj_login(request, user)
            messages.success(request, "Sign in successful.")
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(
                request,
                "The sign in link was invalid or has expired. Please try to sign in again.",
            )
    elif request.method == "POST":
        # The user has submitted the email form.
        form = EmailForm(request.POST)
        if form.is_valid():
            email_login_link(request, form.cleaned_data["email"])
            messages.success(
                request,
                "Email sent! Please check your inbox and click on the link to sign in.",
            )
        else:
            messages.error(
                request,
                "The email address was invalid. Please check the address and try again.",
            )
    else:
        messages.error(
            request,
            "The sign in link was invalid or has expired. Please try to sign in again.",
        )

    return redirect(settings.LOGIN_URL)


@require_safe
@login_required
def logout(request):
    dj_logout(request)
    # messages.success(request, "You have been logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def company_new(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = form.save(commit=False)
            new_route = shortuuid.ShortUUID(
                "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
            ).random(length=6)
            new_company.save()
            request.user.profile.company = new_company
            request.user.save()
            return redirect("main:billing_setup")
    else:
        form = CompanyForm()

    return render(request, "main/company_new.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_setup(request):
    return render(request, "main/billing_setup.html")


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_customer(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        stripe_customer = billing.customer_create(request.user.email, data["token"])
        request.user.profile.stripe_id = stripe_customer.id
        request.user.save()
        return redirect("main:index")


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def profile(request, route, username):
    if not username:
        company = Company.objects.get(route=route)
        return render(request, "main/profile.html", {"company": company})
    else:
        user = User.objects.get(username=username)
        company = Company.objects.get(route=route)
        return render(request, "main/profile.html", {"company": company, "user": user})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def profile_photo(request, route):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        request.user.profile.photo = data["photo_url"]
        request.user.save()
        return redirect(
            "main:profile", request.user.profile.company.route, request.user.username
        )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def company_logo(request, route):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        request.user.profile.company.logo = data["logo_url"]
        request.user.profile.company.save()
        return redirect("main:settings_company", request.user.profile.company.route)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def settings_user(request, route):
    if request.method == "POST":
        form = UserSettingsForm(
            request.POST,
            instance=request.user,
            initial={"slack": request.user.profile.slack},
        )
        if form.is_valid():
            request.user.profile.slack = form.cleaned_data["slack"]
            request.user.save()
            messages.success(request, "User settings updated!")
            return redirect("main:profile", route, request.user.username)
    else:
        form = UserSettingsForm(
            instance=request.user, initial={"slack": request.user.profile.slack}
        )

    return render(request, "main/settings.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def settings_company(request, route):
    if not request.user.profile.is_admin:
        return redirect("main:settings_user", request.user.profile.company.route)

    if request.method == "POST":
        form = CompanySettingsForm(request.POST, instance=request.user.profile.company)
        if form.is_valid():
            request.user.profile.company.save()
            messages.success(request, "Company settings updated!")
            return redirect("main:profile", route, request.user.username)
    else:
        form = CompanySettingsForm(instance=request.user.profile.company)

    return render(request, "main/settings_company.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def invite(request, route):
    company = Company.objects.get(route=route)
    UserFormSet = formset_factory(UserForm, max_num=100, extra=100)
    if request.method == "POST":
        formset = UserFormSet(request.POST, prefix="user")
        if formset.is_valid():
            for form in formset:
                if "email" in form.cleaned_data:
                    data = get_invite_data(request, form.cleaned_data["email"], company)
                    invite_task.delay(data)
            messages.success(request, "Invites sent!")
            return redirect("main:index")
        else:
            messages.error(request, "Invalid email address.")
    else:
        formset = UserFormSet(prefix="user")

    return render(request, "main/invite.html", {"formset": formset, "company": company})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def invite_verify(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already registered.")
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get("d"):
        user = verify_invite_data(token=request.GET["d"])
        if user is not None:
            messages.success(request, "Your account was created succesfully.")
            return redirect(settings.LOGIN_URL)
        else:
            messages.error(request, "Invalid invite link.")
    else:
        messages.error(request, "Invalid invite link.")

    return redirect(settings.LOGIN_URL)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources(request, route):
    return render(request, "main/resources.html")


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions(request, route):
    return render(request, "main/questions.html")
