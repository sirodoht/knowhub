from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from knowhub import settings

from .forms import EmailForm
from .helpers import email_login_link


def index(request):
    if request.user.is_authenticated:
        return render(request, 'main/dashboard.html')
    else:
        return render(request, 'main/index.html')


@require_safe
def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    return render(request, 'main/login.html', {
        'next': request.GET.get('next'),
    })


@require_http_methods(['HEAD', 'GET', 'POST'])
def token_post(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already signed in.')
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.GET.get('d'):
        # The user has clicked a login link.
        user = authenticate(token=request.GET['d'])
        if user is not None:
            dj_login(request, user)
            messages.success(request, 'Sign in successful.')
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, 'The sign in link was invalid or has expired. Please try to sign in again.')
    elif request.method == 'POST':
        # The user has submitted the email form.
        form = EmailForm(request.POST)
        if form.is_valid():
            email_login_link(request, form.cleaned_data['email'])
            messages.success(request, 'Email sent! Please check your inbox and click on the link to sign in.')
        else:
            messages.error(request, 'The email address was invalid. Please check the address and try again.')
    else:
        messages.error(request, 'The sign in link was invalid or has expired. Please try to sign in again.')

    return redirect(settings.LOGIN_URL)


@require_safe
@login_required
def logout(request):
    dj_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect(settings.LOGOUT_REDIRECT_URL)
