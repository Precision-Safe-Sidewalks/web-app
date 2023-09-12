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


@register.simple_tag(takes_context=True)
def get_spec(context, spec_type, spec):
    """Return the InstructionSpecification object if it exists"""
    return (
        context["instruction"]
        .specifications.filter(specification_type=spec_type, specification=spec)
        .first()
    )
