# app/templatetags/custom_filters.py
from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

@register.filter(name='indian_comma')
def indian_comma(value):
    if value is None:
        return ''
    try:
        value = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        return ''

    # split into rupees & paise
    rupees = int(value)
    paise = int((value - rupees) * 100)

    # Indian comma grouping
    rupee_str = str(rupees)[::-1]
    groups = [rupee_str[:3]] + [rupee_str[i:i+2] for i in range(3, len(rupee_str), 2)]
    rupee_part = ','.join(groups)[::-1]

    # add paise only if non-zero
    if paise == 0:
        return rupee_part
    else:
        return f'{rupee_part}.{paise:02d}'