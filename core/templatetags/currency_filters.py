from django import template

register = template.Library()

@register.filter
def ugx(value):
    """Format value as UGX currency"""
    try:
        return f"UGX {float(value):,.0f}"
    except (ValueError, TypeError):
        return "UGX 0"

@register.filter
def currency(value):
    """Format value as currency (alias for ugx)"""
    return ugx(value)
