import datetime
import json

import pytz
import shortuuid
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_safe

from knowhub import settings

from . import billing
from .forms import (
    AnnounceForm,
    AnswerForm,
    CompanyForm,
    CompanySettingsForm,
    DeleteQuestionForm,
    DeleteResourceForm,
    EmailForm,
    ExplorerForm,
    InviteSetupForm,
    ProfileForm,
    QuestionForm,
    ResourceForm,
    SubscriberForm,
    UserForm,
)
from .helpers import (
    email_login_link,
    get_client_ip,
    get_invite_data,
    get_timezones_form,
    log_analytic,
    verify_invite_data,
)
from .models import Answer, Company, Post, Question, Resource, Subscriber, Tag
from .tasks import announce_task, invite_task


def index(request):
    log_analytic(request)
    if request.user.is_authenticated:
        if not request.user.profile.company:
            return redirect("main:company_new")
        if request.user.profile.is_admin and not request.user.profile.stripe_id:
            return redirect("main:billing_setup")
        return redirect("main:questions")
    else:
        return render(request, "main/landing.html")


def people(request):
    if request.user.is_authenticated:
        if request.user.profile.is_admin and not request.user.profile.stripe_id:
            return redirect("main:billing_setup")
        company = Company.objects.get(route=request.user.profile.company.route)
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
        messages.error(request, "You are already signed in")
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get("d"):
        user = authenticate(request, token=request.GET["d"])
        if user is not None:
            dj_login(request, user)
            messages.success(request, "Sign in successful")
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(
                request, "The sign in link was invalid. Please try to sign in again."
            )
    elif request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            if (
                "/signin/" in request.META["HTTP_REFERER"]
                and not User.objects.filter(email=form.cleaned_data["email"]).exists()
            ):
                messages.success(
                    request,
                    "It seems there is no account with this email address. Please try again.",
                )
                return redirect(settings.LOGIN_URL)
            email_login_link(request, form.cleaned_data["email"])
            if User.objects.filter(email=form.cleaned_data["email"]).exists():
                messages.success(
                    request,
                    "Email sent! Check your inbox and click on the link to sign in.",
                )
            else:
                messages.success(
                    request, "Email sent! Check your inbox to get started."
                )
        else:
            messages.error(
                request,
                "The email address was invalid. Please check the address and try again.",
            )
    else:
        messages.error(
            request, "The sign in link was invalid. Please try to sign in again."
        )

    return redirect(settings.LOGIN_URL)


@require_safe
@login_required
def logout(request):
    dj_logout(request)
    messages.success(request, "You have been logged out")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def invite(request):
    company = Company.objects.get(route=request.user.profile.company.route)
    UserFormSet = formset_factory(UserForm, max_num=100, extra=100)
    if request.method == "POST":
        formset = UserFormSet(request.POST, prefix="user")
        if formset.is_valid():
            unique_emails = []
            for form in formset:
                if (
                    "email" in form.cleaned_data
                    and form.cleaned_data["email"] not in unique_emails
                ):
                    unique_emails.append(form.cleaned_data["email"])
            for email in unique_emails:
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
                return redirect("main:invite_setup")
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
def invite_setup(request):
    if request.user.profile.name:
        return redirect("main:profile", request.user.username)

    if request.method == "POST":
        form = InviteSetupForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Welcome!")
            return redirect("main:index")
    else:
        form = InviteSetupForm(instance=request.user.profile)

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
            return redirect("main:billing_setup")
    else:
        form = CompanyForm()

    return render(request, "main/company_new.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_setup(request):
    stripe_public = settings.STRIPE_PUBLIC
    return render(request, "main/billing_setup.html", {"stripe_public": stripe_public})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def billing_customer(request):
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
def profile(request, username):
    if not username:
        company = Company.objects.get(route=request.user.profile.company.route)
        return render(request, "main/profile.html", {"company": company})
    else:
        user = User.objects.get(username=username)
        local_time = datetime.datetime.now(
            pytz.timezone(user.profile.time_zone)
        ).strftime("%H:%M")
        local_datetime = datetime.datetime.now(
            pytz.timezone(user.profile.time_zone)
        ).strftime("%a, %b %-d - %-I:%M %p")
        if user.profile.work_start:
            user_timezone = pytz.timezone(user.profile.time_zone)
            now = timezone.now()
            user.profile.work_start = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=user.profile.work_start.hour,
                minute=user.profile.work_end.minute,
            )
            localized = user_timezone.localize(user.profile.work_start)
            user.profile.work_start = localized.astimezone(
                pytz.timezone(request.user.profile.time_zone)
            )
        if user.profile.work_end:
            user_timezone = pytz.timezone(user.profile.time_zone)
            now = timezone.now()
            user.profile.work_end = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=user.profile.work_end.hour,
                minute=user.profile.work_end.minute,
            )
            localized = user_timezone.localize(user.profile.work_end)
            user.profile.work_end = localized.astimezone(
                pytz.timezone(request.user.profile.time_zone)
            )
        company = Company.objects.get(route=request.user.profile.company.route)
        return render(
            request,
            "main/profile.html",
            {
                "company": company,
                "user": user,
                "local_time": local_time,
                "local_datetime": local_datetime,
            },
        )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def profile_photo(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        request.user.profile.photo = data["photo_url"]
        request.user.save()
        return JsonResponse(status=200, data={"message": "Success!"})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def company_logo(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)
        request.user.profile.company.logo = data["logo_url"]
        request.user.profile.company.save()
        return JsonResponse(status=200, data={"message": "Success!"})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def settings_user(request):
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            instance=request.user.profile,
            initial={"email": request.user.email, "username": request.user.username},
        )
        if form.is_valid():
            request.user.email = form.cleaned_data["email"]
            request.user.username = form.cleaned_data["username"]
            request.user.save()
            messages.success(request, "Settings updated successfully")
            return redirect("main:profile", request.user.username)
        else:
            messages.success(request, "Settings update failed")
            return redirect("main:profile", request.user.username)
    else:
        initial_data = {"email": request.user.email, "username": request.user.username}
        if request.user.profile.work_start and request.user.profile.work_end:
            initial_data["work_start"] = request.user.profile.work_start.strftime(
                "%H:%M"
            )
            initial_data["work_end"] = request.user.profile.work_end.strftime("%H:%M")
        form = ProfileForm(instance=request.user.profile, initial=initial_data)

    return render(
        request,
        "main/settings_user.html",
        {"form": form, "timezones": get_timezones_form()},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def settings_company(request):
    if not request.user.profile.is_admin:
        return redirect("main:settings_user")

    if request.method == "POST":
        form = CompanySettingsForm(request.POST, instance=request.user.profile.company)
        if form.is_valid():
            request.user.profile.company.save()
            messages.success(request, "Settings updated successfully")
            return redirect("main:profile", request.user.username)
    else:
        form = CompanySettingsForm(instance=request.user.profile.company)

    return render(request, "main/settings_company.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources(request):
    resources = Resource.objects.filter(company=request.user.profile.company).order_by(
        "title"
    )
    return render(request, "main/resources.html", {"resources": resources})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources_view(request, resource_slug):
    resource = Resource.objects.get(slug=resource_slug)
    return render(request, "main/resources_view.html", {"resource": resource})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources_create(request):
    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.company = request.user.profile.company
            resource.slug = slugify(form.cleaned_data["title"])
            resource.slug += "-" + shortuuid.ShortUUID(
                "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
            ).random(length=6)
            resource.save()
            for tag_text in form.cleaned_data["tags"].split(","):
                if tag_text.strip():
                    tag, created = Tag.objects.get_or_create(text=tag_text)
                    tag.resources.add(resource)
            return redirect("main:resources_view", resource.slug)
        else:
            messages.error(request, "Resource creation failed")
            return redirect("main:resources")
    else:
        form = ResourceForm()

    return render(request, "main/resources_create.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def resources_edit(request, resource_slug):
    resource = Resource.objects.get(slug=resource_slug)
    if request.method == "POST":
        form = ResourceForm(
            request.POST, instance=resource, initial={"tags": resource.tags}
        )
        if form.is_valid():
            resource = form.save(commit=False)
            if "title" in form.changed_data:
                resource.slug = slugify(form.cleaned_data["title"])
                resource.slug += "-" + shortuuid.ShortUUID(
                    "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
                ).random(length=6)
            resource.save()
            resource.tag_set.clear()
            for tag_text in form.cleaned_data["tags"].split(","):
                if tag_text.strip():
                    tag, created = Tag.objects.get_or_create(text=tag_text)
                    tag.resources.add(resource)
            return redirect("main:resources_view", resource.slug)
        else:
            messages.error(request, "Resource editing failed")
            return redirect("main:resources_view", resource_slug)
    else:
        resource = Resource.objects.get(slug=resource_slug)
        form = ResourceForm(instance=resource, initial={"tags": resource.tags})

    return render(
        request, "main/resources_edit.html", {"form": form, "resource": resource}
    )


@require_http_methods(["HEAD", "POST"])
@login_required
def resources_delete(request, resource_slug):
    if request.method == "POST":
        resource = Resource.objects.get(slug=resource_slug)
        form = DeleteResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource.delete()
            return redirect("main:resources")
            messages.success(request, "Resource deleted successfully")
        else:
            messages.error(request, "Resource deletion failed")
            return redirect("main:resources_view", resource_slug)


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions(request):
    questions = Question.objects.filter(company=request.user.profile.company).order_by(
        "-updated_at"
    )
    return render(request, "main/questions.html", {"questions": questions})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions_view(request, question_slug):
    question = Question.objects.get(slug=question_slug)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            send_mail(
                "Re: " + question.title,
                render_to_string(
                    "main/answer_notification_email.txt",
                    {
                        "current_site": get_current_site(request),
                        "body": answer.body,
                        "question_link": reverse(
                            "main:questions_view", args=[question.slug]
                        ),
                    },
                    request=request,
                ),
                settings.DEFAULT_FROM_EMAIL,
                [question.author.email],
            )
            return redirect("main:questions_view", question_slug)
        else:
            messages.error(request, "Question posting failed")
            return redirect("main:questions_view", question_slug)
    else:
        form = AnswerForm()
        answers = Answer.objects.filter(question=question).order_by("created_at")

    return render(
        request,
        "main/questions_view.html",
        {"form": form, "question": question, "answers": answers},
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.company = request.user.profile.company
            question.slug = slugify(form.cleaned_data["title"])
            question.slug += "-" + shortuuid.ShortUUID(
                "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
            ).random(length=6)
            question.save()
            return redirect("main:questions_view", question.slug)
        else:
            messages.error(request, "Question posting failed.")
            return redirect("main:questions")
    else:
        form = QuestionForm()

    return render(request, "main/questions_create.html", {"form": form})


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions_edit(request, question_slug):
    question = Question.objects.get(slug=question_slug)
    if request.user != question.author:
        return redirect("main:questions")
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            if "title" in form.changed_data:
                question.slug = slugify(form.cleaned_data["title"])
                question.slug += "-" + shortuuid.ShortUUID(
                    "abdcefghkmnpqrstuvwxyzABDCEFGHKMNPQRSTUVWXYZ23456789"
                ).random(length=6)
            question.save()
            return redirect("main:questions_view", question.slug)
        else:
            messages.error(request, "Question posting failed")
            return redirect("main:questions")
    else:
        form = QuestionForm(instance=question)

    return render(
        request, "main/questions_edit.html", {"form": form, "question": question}
    )


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def questions_delete(request, question_slug):
    if request.method == "POST":
        question = Question.objects.get(slug=question_slug)
        if request.user != question.author:
            return redirect("main:questions")
        form = DeleteQuestionForm(request.POST, instance=question)
        if form.is_valid():
            question.delete()
            messages.success(request, "Question deleted successfully")
            return redirect("main:questions")
        else:
            messages.error(request, "Question deletion failed")
            return redirect("main:questions_view", question_slug)


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


@require_safe
def terms(request):
    return render(request, "main/terms.html")


@require_safe
def privacy(request):
    return render(request, "main/privacy.html")


@require_http_methods(["HEAD", "GET", "POST"])
@login_required
def announce(request):
    if request.method == "POST":
        form = AnnounceForm(request.POST)
        if form.is_valid():
            profiles = request.user.profile.company.profile_set.all()
            for item in profiles:
                announce_task.delay(
                    {
                        "subject": form.cleaned_data["subject"],
                        "body": form.cleaned_data["body"],
                        "email": item.user.email,
                    }
                )
            messages.success(request, "Announcement emails sent")
            return redirect("main:people")
        else:
            messages.error(request, "Invalid input data")
    else:
        form = AnnounceForm()

    return render(request, "main/announce.html", {"form": form})
