"""Managers keep the carousel of the shop in the management interface; the shop shows it with the carousel_show
tag. Visitors without the manage_shop permission cannot change it."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.template import Context, Template
from django.urls import reverse

from lfs.core.models import Shop
from lfs_carousel.models import CarouselItem


@pytest.fixture
def shop(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    return Shop.objects.get()


@pytest.fixture
def item(shop):
    return CarouselItem.objects.create(
        content=shop, title="Summer sale", link="https://example.com/sale", text="All garden tools", position=10
    )


@pytest.fixture
def manager(client, shop):
    client.force_login(get_user_model().objects.create_superuser("admin", "admin@example.com", "x"))
    return client


def update_url(shop):
    return reverse("lfs_carousel_update_items", args=[ContentType.objects.get_for_model(shop).pk, shop.pk])


def test_shop_management_has_a_carousel_tab_listing_the_items(manager, item):
    html = manager.get(reverse("lfs_manage_shop_carousel")).content.decode()

    assert 'value="Summer sale"' in html


def test_manager_updates_title_and_text_of_an_item(manager, shop, item):
    manager.post(update_url(shop), {"action": "update", f"title-{item.id}": "Winter sale", f"text-{item.id}": "Sledges"})

    item.refresh_from_db()
    assert (item.title, item.text) == ("Winter sale", "Sledges")


def test_manager_deletes_an_item(manager, shop, item):
    manager.post(update_url(shop), {"action": "delete", f"delete-{item.id}": "on"})

    assert not CarouselItem.objects.exists()


def test_visitor_without_permission_is_sent_to_the_login_and_changes_nothing(client, shop, item):
    response = client.post(update_url(shop), {"action": "delete", f"delete-{item.id}": "on"})

    assert response.status_code == 302 and reverse("lfs_login") in response["Location"]
    assert CarouselItem.objects.filter(pk=item.pk).exists()


def test_visitor_cannot_reorder_items(client, shop, item):
    client.get(f"/carousel/move-item/{item.id}?direction=1")

    item.refresh_from_db()
    assert item.position == 10


def test_carousel_show_renders_the_items_without_a_theme(shop, item):
    html = Template("{% load lfs_carousel_tags %}{% carousel_show shop %}").render(Context({"shop": shop}))

    assert "Summer sale" in html and 'href="https://example.com/sale"' in html and "All garden tools" in html


def test_carousel_show_renders_nothing_without_items(shop):
    html = Template("{% load lfs_carousel_tags %}{% carousel_show shop %}").render(Context({"shop": shop}))

    assert html.strip() == ""
