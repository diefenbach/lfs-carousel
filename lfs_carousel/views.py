# -*- coding: utf-8 -*-
from functools import update_wrapper
import json

# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

# lfs.imports
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder

# lfs_carousel imports
from lfs_carousel.models import CarouselItem
from lfs_carousel.signals import carousel_changed

# Load logger
import logging

logger = logging.getLogger("lfs")


class LFSCarouselView(object):
    def refresh_positions(self, ct, object_id):
        """order items"""
        items = self.get_item_cls().objects.filter(content_type=ct, content_id=object_id)
        for i, item in enumerate(items):
            item.position = (i + 1) * 10
            item.save()

    def get_item_cls(self):
        """return model Class used by Carousel"""
        return CarouselItem

    def manage_items(
        self, request, content_type_id, object_id, as_string=False, template_name="lfs_carousel/items.html"
    ):
        """ """
        ct = lfs_get_object_or_404(ContentType, pk=content_type_id)
        obj = ct.get_object_for_this_type(pk=object_id)

        items = self.get_item_cls().objects.filter(content_type=ct, content_id=object_id)

        result = render_to_string(template_name, {"obj": obj, "ct": ct, "items": items}, request=request)

        if as_string:
            return result
        else:
            result = json.dumps(
                {
                    "items": result,
                    "message": _("Carousel items have been added."),
                },
                cls=LazyEncoder,
            )

            return HttpResponse(result)

    def list_items(
        self, request, content_type_id, object_id, as_string=False, template_name="lfs_carousel/items-list.html"
    ):
        """ """

        result = self.manage_items(request, content_type_id, object_id, as_string=True, template_name=template_name)

        if as_string:
            return result
        else:
            result = json.dumps(
                {
                    "items": result,
                    "message": _("Carousel items have been added."),
                },
                cls=LazyEncoder,
            )

            return HttpResponse(result, content_type="application/json")

    def add_item(self, request, content_type_id, object_id):
        """Adds an image/carousel item to object"""
        ct = lfs_get_object_or_404(ContentType, pk=content_type_id)
        obj = ct.get_object_for_this_type(pk=object_id)

        if request.method == "POST":
            for file_content in request.FILES.getlist("files[]"):
                item = self.get_item_cls()(content=obj)
                try:
                    item.image.save(file_content.name, file_content, save=True)
                except Exception as e:
                    logger.info("Upload item: %s %s" % (file_content.name, e))
                    continue

        self.refresh_positions(ct, object_id)

        carousel_changed.send(obj, request=request)

        result = json.dumps({"name": file_content.name, "type": "image/jpeg", "size": "123456789"})
        return HttpResponse(result)

    def update_items(self, request, content_type_id, object_id):
        """Saves/deletes items with given ids (passed by request body)."""
        ct = lfs_get_object_or_404(ContentType, pk=content_type_id)
        obj = ct.get_object_for_this_type(pk=object_id)

        action = request.POST.get("action")
        if action == "delete":
            message = _("Carousel items have been deleted.")
            for key in request.POST.keys():
                if key.startswith("delete-"):
                    try:
                        item_id = key.split("-")[1]
                        self.get_item_cls().objects.get(pk=item_id).delete()
                    except (IndexError, ObjectDoesNotExist):
                        pass

        elif action == "update":
            message = _("Carousel items have been updated.")
            for key, value in request.POST.items():
                if not "-" in key:
                    continue
                id = key.split("-")[1]
                try:
                    item = self.get_item_cls().objects.get(pk=id)
                except ObjectDoesNotExist:
                    pass
                else:
                    if key.startswith("title-"):
                        item.title = value
                        item.save()
                    elif key.startswith("position-"):
                        item.position = value
                        item.save()
                    elif key.startswith("link-"):
                        item.link = value
                        item.save()
                    elif key.startswith("text-"):
                        item.text = value
                        item.save()

        self.refresh_positions(ct, object_id)

        carousel_changed.send(obj, request=request)

        html = [["#items-list", self.list_items(request, content_type_id, object_id, as_string=True)]]
        result = json.dumps(
            {
                "html": html,
                "message": message,
            },
            cls=LazyEncoder,
        )

        return HttpResponse(result, content_type="application/json")

    def move_item(self, request, id):
        """Moves the items with passed id up or down.

        **Parameters:**
            id
                The id of the item which should be edited.

        **Query String:**
            direction
                The direction in which the item should be moved. One of 0 (up)
                or 1 (down).

        **Permission:**
            edit (of the belonging content object)
        """
        item = self.get_item_cls().objects.get(pk=id)
        obj = item.content

        direction = request.GET.get("direction", 0)

        if direction == "1":
            item.position += 15
        else:
            item.position -= 15
            if item.position < 0:
                item.position = 10

        item.save()

        ct = ContentType.objects.get_for_model(obj)

        self.refresh_positions(ct, obj.pk)

        html = [["#items-list", self.list_items(request, ct.pk, obj.pk, as_string=True)]]

        result = json.dumps(
            {
                "html": html,
            },
            cls=LazyEncoder,
        )

        return HttpResponse(result)

    # copied from contrib.admin.sites
    def has_permission(self, request):
        """Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active and request.user.has_perm("core.manage_shop")

    def carousel_view(self, view, cacheable=False):
        """Decorator to create an carousel view attached to this ``LFSCarousel``. This
        wraps the view and provides permission checking by calling
        ``self.has_permission``.
        """

        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                return HttpResponseRedirect("%s?next=%s" % (reverse("django.contrib.auth.views.login"), request.path))
            return view(request, *args, **kwargs)

        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, "csrf_exempt", False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def get_urls(self):
        from django.urls import include, re_path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.carousel_view(view, cacheable)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            re_path(
                r"^add-item/(?P<content_type_id>\d*)/(?P<object_id>\d*)/$",
                wrap(self.add_item),
                name="lfs_carousel_add_item",
            ),
            re_path(
                r"^update-items/(?P<content_type_id>\d*)/(?P<object_id>\d*)/$",
                wrap(self.update_items),
                name="lfs_carousel_update_items",
            ),
            re_path(
                r"^manage-items/(?P<content_type_id>\d*)/(?P<object_id>\d*)/$",
                wrap(self.list_items),
                name="lfs_carousel_manage_items",
            ),
            re_path(r"^move-item/(?P<id>\d+)$", self.move_item, name="lfs_carousel_move_item"),
        ]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()


carousel = LFSCarouselView()
