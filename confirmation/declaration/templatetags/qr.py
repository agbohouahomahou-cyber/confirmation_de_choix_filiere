
import segno
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def qr_svg(data, scale=4):
    """Renvoie un vrai QR code en SVG inline, aux couleurs de la charte."""
    qr = segno.make(data, error="m")
    return mark_safe(qr.svg_inline(scale=scale, border=0, dark="#0F3D2E", title="QR code de vérification"))
