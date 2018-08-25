import pytz
import time
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


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
