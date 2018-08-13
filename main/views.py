import json

import shortuuid
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_safe

from knowhub import settings

from . import billing
from .forms import (
    CompanyForm,
    CompanySettingsForm,
    EmailForm,
    ExplorerForm,
    ResourceForm,
    SubscriberForm,
    UserForm,
    UserSettingsForm,
    UserSetupForm,
)
from .helpers import (
    email_login_link,
    get_client_ip,
    get_invite_data,
    log_analytic,
    verify_invite_data,
)
from .models import Company, Post, Resource, Subscriber
from .tasks import invite_task


def index(request):
    log_analytic(request)
    if request.user.is_authenticated:
        if not request.user.profile.company:
            return redirect("main:company_new")
        if request.user.profile.is_admin and not request.user.profile.stripe_id:
            return redirect("main:billing_setup", request.user.profile.company.route)
        return redirect("main:people", request.user.profile.company.route)
    else:
        return render(request, "main/marketing.html")


def company(request, route):
    return redirect("main:index")


def people(request, route):
    if request.user.is_authenticated:
        if request.user.profile.is_admin and not request.user.profile.stripe_id:
            return redirect("main:billing_setup", route)
        company = Company.objects.get(route=route)
        people = User.objects.all().filter(
            profile__company=request.user.profile.company
        )
        return render(
            request, "main/people.html", {"company": company, "people": people}
        )
    else:
        return redirect("main:index")


@require_safe
def register(request):
    log_analytic(request)
    if request.user.is_authenticated:
        return redirect("main:index")
    return render(request, "main/register.html")


@require_safe
def login(request):
    log_analytic(request)
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
        user = authenticate(request, token=request.GET["d"])
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
def invite(request, route):
    company = Company.objects.get(route=route)
    UserFormSet = formset_factory(UserForm, max_num=100, extra=100)
    if request.method == "POST":
        formset = UserFormSet(request.POST, prefix="user")
        if formset.is_valid():
            uniqueEmails = []
            for form in formset:
                if (
                    "email" in form.cleaned_data
                    and form.cleaned_data["email"] not in uniqueEmails
                ):
                    uniqueEmails.append(form.cleaned_data["email"])
            for email in uniqueEmails:
                data = get_invite_data(request, email, company)
                invite_task.delay(data)
            messages.success(request, "Invites sent!")
            return redirect("main:index")
        else:
            messages.error(request, "Invalid email address.")
    else:
        formset = UserFormSet(prefix="user")

    return render(request, "main/invite.html", {"formset": formset, "company": company})


@require_http_methods(["HEAD", "GET", "POST"])
def invite_verify(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already registered and logged in.")
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get("d"):
        user = verify_invite_data(token=request.GET["d"])
        if user is not None:
            messages.success(request, "Your account was created succesfully.")
            user = authenticate(request, token=request.GET["d"])
            if user is not None:
                dj_login(request, user)
                billing.subscription_upgrade(request.user)
                return redirect("main:invite_setup", user.profile.company.route)
            else:
                messages.error(
                    request,
                    "The sign in link was invalid or has expired. Please try to sign in again.",
                )
            return redirect(settings.LOGIN_URL)
        else:
            messages.error(request, "Invalid invite link.")
    else:
        messages.error(request, "Invalid invite link.")

    return redirect(settings.LOGIN_URL)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def invite_setup(request, route):
    if request.user.profile.name:
        return redirect("main:profile", route, request.user.username)

    if request.method == "POST":
        form = UserSetupForm(request.POST, instance=request.user)
        if form.is_valid():
            request.user.profile.name = form.cleaned_data["name"]
            request.user.profile.slack = form.cleaned_data["slack"]
            request.user.profile.role = form.cleaned_data["role"]
            request.user.save()
            messages.success(request, "Welcome!")
            return redirect("main:index")
    else:
        form = UserSetupForm(instance=request.user)

    return render(request, "main/invite_setup.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def company_new(request):
    log_analytic(request)
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = form.save(commit=False)
            new_route = shortuuid.ShortUUID(
                "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
            ).random(length=6)
            new_route = [new_route[i : i + 2] for i in range(0, len(new_route), 2)]
            new_company.route = "-".join(new_route)
            new_company.save()
            request.user.profile.company = new_company
            request.user.profile.is_admin = True
            request.user.save()
            return redirect("main:billing_setup", request.user.profile.company.route)
    else:
        form = CompanyForm()

    return render(request, "main/company_new.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_setup(request, route):
    if route != request.user.profile.company.route:
        return redirect("main:index")
    stripe_public = settings.STRIPE_PUBLIC
    return render(request, "main/billing_setup.html", {"stripe_public": stripe_public})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_customer(request, route):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        stripe_customer = billing.customer_create(request.user.email, data["token"])
        billing.subscription_create(stripe_customer.id)
        request.user.profile.stripe_id = stripe_customer.id
        request.user.save()
        return redirect("main:index")


@require_http_methods(["HEAD", "GET", "POST"])
def subscribe(request):
    if request.user.is_authenticated:
        return redirect("main:index")
    if request.method == "POST":
        log_analytic(request)
        form = ExplorerForm(request.POST)
        if form.is_valid():
            explorer = form.save(commit=False)
            explorer.ip = get_client_ip(request)
            explorer.save()
            send_mail(
                "Explorer signup at KnowHub",
                explorer.email + " just signed up!",
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMINS[0][1]],
            )
            return redirect("main:subscribe_thanks")
    else:
        log_analytic(request)
        form = ExplorerForm()

    return render(request, "main/subscribe.html", {"form": form})


@require_safe
def subscribe_thanks(request):
    log_analytic(request)
    if request.user.is_authenticated:
        return redirect("main:index")
    return render(request, "main/subscribe_thanks.html")


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
def resources(request, route):
    resources = Resource.objects.filter(company=request.user.profile.company).order_by(
        "title"
    )
    return render(request, "main/resources.html", {"resources": resources})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources_view(request, route, document):
    resource = Resource.objects.get(slug=document)
    return render(request, "main/resources_document.html", {"resource": resource})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources_create(request, route):
    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.company = request.user.profile.company
            resource.slug = slugify(form.cleaned_data["title"])
            if resource.slug == "new":
                resource.slug = "new-" + shortuuid.ShortUUID(
                    "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
                ).random(length=6)
            resource.save()
            messages.success(request, "Resource created.")
            return redirect("main:resources", route)
        else:
            messages.error(request, "Resource creation failed.")
            return redirect("main:resources", route)
    else:
        form = ResourceForm()

    return render(request, "main/resources_create.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions(request, route):
    return render(request, "main/questions.html")


@require_safe
def blog(request):
    log_analytic(request)
    posts = Post.objects.all().order_by("-date")
    return render(request, "main/blog.html", {"posts": posts})


@require_safe
def blog_post(request, post_slug):
    log_analytic(request)
    post = Post.objects.get(slug=post_slug)
    return render(request, "main/blog_post.html", {"post": post})


@require_http_methods(["POST"])
def blog_subscribe(request):
    log_analytic(request)
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber, created = Subscriber.objects.get_or_create(
                email=form.cleaned_data["email"]
            )
            if created:
                subscriber.ip = get_client_ip(request)
                subscriber.save()
                return JsonResponse(status=200, data={"message": "Success!"})
            else:
                return JsonResponse(status=200, data={"message": "Already subscribed!"})
        else:
            return JsonResponse(
                status=400, data={"message": "Something went wrong. Sorry about that."}
            )


@require_safe
def google_verify(request):
    return render(request, "main/googlef6b7b346eca71466.html")


def terms(request):
    return render(request, "main/terms.html")


def privacy(request):
    return render(request, "main/privacy.html")
