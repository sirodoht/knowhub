import time

import pytz
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .helpers import log_analytic


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            timezone.activate(pytz.timezone(request.user.profile.time_zone))
        else:
            timezone.deactivate()


class StatsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        total = time.time() - request.start_time
        response["X-Total-Time"] = int(total * 1000)
        return response


class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "pomplamoose" not in request.path:
            log_analytic(request)


class BillingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (
            request.user.is_authenticated
            and request.path != "/billing/"
            and request.path != "/billing/customer/"
        ):
            if request.user.profile.is_admin and not request.user.profile.stripe_id:
                return redirect("main:billing_setup")
