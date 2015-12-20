from django import template
from django.template.defaultfilters import stringfilter

import geoip2.database
from django.conf import settings
from os.path import join

geoip2reader = geoip2.database.Reader(join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY))

register = template.Library()

@register.filter
def get_client_ip(request_object):
    x_forwarded_for = request_object.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request_object.META.get('REMOTE_ADDR')
    return ip

@register.filter
def get_country_by_ip(request_object):
    ip_address = get_client_ip(request_object)
    try:
        return geoip2reader.country(ip_address).country.iso_code
    except:
        return 'XX'
