from django import template

register = template.Library()


@register.filter
def isin(value, options):
    """Return True if the value is in the options"""
    print(value, type(value))
    print(options, type(options))
    if isinstance(options, list):
        return value in options
    return str(value) == str(options)
