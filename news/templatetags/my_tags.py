from datetime import datetime

from django import template


register = template.Library()

@register.simple_tag
def url_replace(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()
