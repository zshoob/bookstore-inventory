from django import template
import re

register = template.Library()

@register.filter
def get_field(field):
    return field
