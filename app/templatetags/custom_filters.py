# app/templatetags/custom_filters.py
from django import template
import locale

register = template.Library()

@register.filter(name='indian_comma')
def indian_comma(value):
    if value is None:
        return ''
    try:
        # Ensure the value is a number
        value = float(value)
        # Set locale to Indian
        locale.setlocale(locale.LC_ALL, 'en_IN')
        return locale.format_string("%d", value, grouping=True)
    except (locale.Error, ValueError, TypeError):
        # Fallback if locale is not available or value is not a number
        return "{:,}".format(value).replace(',', 'X').replace('.', ',').replace('X', '.')