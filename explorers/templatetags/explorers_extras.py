from django import template

register = template.Library()


# Generate possessive form of a word
# ex: Return `Mark's` from Mark
# ex: Return `Chavez'` from Chavez
@register.filter(name='possessive')
def possessive(value):
    if value[-1] in 'sz':
        return '{0}\''.format(value)
    return '{0}\'s'.format(value)
