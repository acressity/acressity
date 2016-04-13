from django import template

register = template.Library()


# Template tag for pluralized possessive
@register.filter(name='possessive')
def possessive(value):
    if value[-1] in 'sz':
        return '{0}\''.format(value)
    return '{0}\'s'.format(value)
