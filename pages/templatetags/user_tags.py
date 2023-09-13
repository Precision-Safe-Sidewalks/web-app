from django import template

register = template.Library()


@register.simple_tag
def has_role(user, role):
    """Return True if the user has the role"""
    print(user, role, user.roles.all().values("role"))
    return user.roles.filter(role=role).exists()
