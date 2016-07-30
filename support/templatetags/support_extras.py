from django import template

from support.models import Quote

register = template.Library()

@register.assignment_tag
def random_quote():
    return Quote.objects.random()
