"""URLs for the add-on's tests: the shop, the management interface, and the carousel."""

from django.urls import include, path

from lfs_carousel.views import carousel

urlpatterns = [
    path("", include("lfs.core.urls")),
    path("manage/", include("lfs.manage.urls")),
    path("carousel/", include(carousel.urls)),
]
