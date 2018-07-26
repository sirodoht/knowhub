import re

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_active(context, pattern):
    path = context["request"].path
    if re.search(pattern, path):
        return "nav-item-active"
    return ""


@register.simple_tag(takes_context=True)
def icon_active(context, pattern):
    path = context["request"].path
    if re.search(pattern, path):
        return "nav-item-icon-active"
    return ""
