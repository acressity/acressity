import re

from django import template
register = template.Library()

# Usage: |replace:"/(re for search)/(re for replace)"


@register.filter
def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, string)
