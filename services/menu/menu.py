from django.db import transaction
from django.db.models import Prefetch, Sum, Count

from django.forms.models import model_to_dict
from algoliasearch.search_client import SearchClient
from django.conf import settings

from menu.models import Menu
from storage.models import (

    InventoryItem)
from orders.models import OrderItem

client = SearchClient.create(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY)
index = client.init_index("menu")


def get_available_ready_made_products(branch_id):
    available_ready_made_products = Menu.objects.filter(
        branch=branch_id, available=True, category__name="Готовые продукты"
    )

    ready_made_products = [model_to_dict(product) for product in available_ready_made_products]
    return ready_made_products


def get_available_items(branch_id):
    all_menu_items = Menu.objects.filter(branch=branch_id, available=True)
    available_menu_items = []

    for item in all_menu_items:
        can_make = True
        for ingredient in item.ingredients.all():
            inventory_item = InventoryItem.objects.filter(
                name=ingredient.name, branch=branch_id).first()
            if not inventory_item or inventory_item.quantity < ingredient.quantity:
                can_make = False
                break

        if can_make:
            item_dict = model_to_dict(item)
            available_menu_items.append(item_dict)

    return available_menu_items


def combine_items_and_ready_made_products(branch_id, category_id=None):
    available_items = get_available_items(branch_id)
    available_ready_made_products = get_available_ready_made_products(branch_id)

    if category_id:
        available_items = [item for item in available_items if item['category_id'] == category_id]
        available_ready_made_products = [product for product in available_ready_made_products if
                                         product['category_id'] == category_id]

    combined_list = available_items + available_ready_made_products
    return combined_list


def get_popular_items(branch_id):
    item_sales = (OrderItem.objects
                  .filter(order__branch_id=branch_id)
                  .values('menu_id')
                  .annotate(total_quantity=Sum('menu_quantity'))
                  .order_by('-total_quantity'))

    popular_items = [{'menu_id': item['menu_id'], 'total_quantity': item['total_quantity']} for item in item_sales][:10]
    return popular_items


def get_complementary_objects(order_item_id):
    order_id = OrderItem.objects.get(id=order_item_id).order.id
    complementary_items = (OrderItem.objects
                           .filter(order_id=order_id)
                           .exclude(id=order_item_id)
                           .values('menu_id')
                           .annotate(count=Count('menu_id'))
                           .order_by('-count')[:3])
    return complementary_items

def get_compatibles(menu_id, branch_id):
    order_ids = OrderItem.objects.filter(menu_id=menu_id, order__branch_id=branch_id).values_list('order_id', flat=True)
    complementary_items = get_complementary_objects(list(order_ids))
    return complementary_items


def update_ingredient_storage_on_cooking(menu_id, branch_id, quantity):
    try:
        with transaction.atomic():
            menu_items = Menu.objects.get(id=menu_id).ingredients.all()
            for item in menu_items:
                inventory_item = InventoryItem.objects.get(name=item.name, branch_id=branch_id)
                inventory_item.quantity -= item.quantity * quantity
                inventory_item.save()
            return "Updated successfully."
    except Exception as e:
        raise e


def check_if_items_can_be_made(menu_id, branch_id, quantity):
    ingredients = Menu.objects.get(id=menu_id).ingredients.all()
    for ingredient in ingredients:
        inventory_item = InventoryItem.objects.get(name=ingredient.name, branch_id=branch_id)
        if inventory_item.quantity < ingredient.quantity * quantity:
            return False
    return True


def item_search(query, branch_id):
    items = index.search(query, {"filters": f"branch_id:{branch_id}"})["hits"]

    return items


