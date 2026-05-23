import base64
from django import template

register = template.Library()

@register.filter
def b64encode(value):
    """Encode bytes into base64 string (за QR code)"""
    return base64.b64encode(value).decode('ascii')
