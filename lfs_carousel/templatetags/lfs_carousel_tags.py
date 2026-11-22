from django.template import Library

from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from lfs_carousel.views import carousel

register = Library()


def _carousel_items(obj, content_type):
    return carousel.get_item_cls().objects.filter(content_type=content_type, content_id=obj.pk)


@register.simple_tag(takes_context=True)
def carousel_management(context, obj):
    request = context.get("request", None)  # we rely on request context processor

    ct = ContentType.objects.get_for_model(obj)

    result = carousel.manage_items(request, ct.pk, obj.pk, as_string=True)
    return mark_safe(result)


@register.inclusion_tag("lfs_carousel/carousel.html", takes_context=True)
def carousel_show(context, obj):
    ct = ContentType.objects.get_for_model(obj)
    items = _carousel_items(obj, ct)
    return {"items": items, "obj": obj, "ct": ct}


@register.simple_tag
def carousel_image_url(request, obj):
    """Return the absolute URL of the first carousel image."""
    ct = ContentType.objects.get_for_model(obj)
    item = _carousel_items(obj, ct).filter(image__isnull=False).exclude(image="").first()
    return request.build_absolute_uri(item.image.url) if item else ""
