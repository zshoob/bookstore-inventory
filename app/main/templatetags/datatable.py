from django import template

register = template.Library()

@register.filter
def get_field(row, col):
    return getattr(row, col)
