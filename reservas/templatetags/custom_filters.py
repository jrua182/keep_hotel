from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(date, days):
    """Añade días a una fecha"""
    try:
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date

@register.filter
def split(value, delimiter):
    """Divide una cadena por un delimitador"""
    return value.split(delimiter)

@register.filter
def strip(value):
    """Elimina espacios al inicio y final"""
    return value.strip() if value else value