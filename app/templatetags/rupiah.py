from django import template

register = template.Library()


@register.filter
def rupiah(nilai):
    """Format angka jadi rupiah gaya Indonesia: 9000 -> '9.000'."""
    try:
        return f"{int(float(nilai)):,}".replace(',', '.')
    except (TypeError, ValueError):
        return nilai
