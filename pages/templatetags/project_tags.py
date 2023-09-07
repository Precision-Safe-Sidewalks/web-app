from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def status_icon(value):
    """Return the HTML icon for the True/False value"""
    if value:
        color = "success"
        icon = "check_circle"
    else:
        color = "warning"
        icon = "warning"

    element = f"""
    <div class="flex--center">
        <span class="icon icon--{color}">{icon}</span>
    </div>
    """

    return mark_safe(element)
