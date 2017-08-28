from django import template
from django.forms import ModelForm
from django.db.models import Model

register = template.Library()

@register.filter
def help_text(obj):
    if isinstance(obj, ModelForm):
        return obj.Meta().model.help_text
    elif isinstance(obj, Model):
        return obj.help_text

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def subtract(value, arg):
    return value - arg

