from django import template

register = template.Library()


@register.filter
def pertenece_grupo(user, grupo):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=grupo).exists()