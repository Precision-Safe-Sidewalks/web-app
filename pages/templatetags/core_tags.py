from django import template

register = template.Library()


@register.filter
def isin(value, options):
    """Return True if the value is in the options"""
    return value in options
