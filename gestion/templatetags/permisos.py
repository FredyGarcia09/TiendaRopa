from django import template

register = template.Library()


@register.filter
def pertenece_grupo(user, grupo):
    return user.groups.filter(name=grupo).exists()