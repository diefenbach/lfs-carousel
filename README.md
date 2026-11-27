# lfs-carousel

An image carousel for [LFS](https://github.com/diefenbach/django-lfs) shops: managers upload images with a title,
text and link in the management interface, and the shop shows them on its start page.

## Requirements

django-lfs 1.0 or newer (Django 5.2, Python 3.12+).

## Installation

```sh
pip install lfs-carousel
```

Add the app and its URLs, then create its table:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "lfs_carousel",
]
```

```python
# urls.py
from lfs_carousel.views import carousel

urlpatterns += [path("carousel/", include(carousel.urls))]
```

```sh
python manage.py migrate
```

## Managing the carousel

With the app installed, the management interface shows a **Carousel** tab under Shop. There managers upload images
(several at once), set each item's title, text, link and position, and delete items. Only users with the
`core.manage_shop` permission can change the carousel; others are sent to the login page.

## Showing the carousel

[lfs-theme](https://github.com/diefenbach/lfs-theme) shows the carousel on the start page as a slider when the app is
installed; nothing else to do.

In your own theme, add the tag where the carousel belongs, usually in `lfs/shop/shop.html`:

```django
{% load lfs_carousel_tags %}
{% carousel_show shop %}
```

It renders `lfs_carousel/carousel.html` with `items` (the carousel items in order of their position). The add-on's
template shows them as a plain list of images with title, text and link; override the template in your theme to turn
them into a slider. Without items it renders nothing.

`{% carousel_image_url request shop %}` returns the absolute URL of the first image, for example for an `og:image`.

## Development

```sh
pip install -e . pytest pytest-django
pytest
```

## License

BSD 3-Clause, see [LICENSE.txt](LICENSE.txt).

## History

- 2.0.0: for django-lfs 1.0 (Django 5.2): management tab in the new management interface, a default template for
  `carousel_show`, visitors without permission are sent to the login page, tests. Removes the coin-slider files and
  the unused, unprotected move-item and manage-items URLs.
- 1.1: Django 1.6 compatibility.
