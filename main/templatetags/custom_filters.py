import datetime

import pytz
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def tz_offset(value):
    offset = datetime.datetime.now(pytz.timezone(value)).strftime("%z")
    return "UTC" + offset[:3] + ":" + offset[3:]
