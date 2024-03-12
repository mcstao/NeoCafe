from django.db import transaction
from rest_framework import status

from menu.models import Menu
from orders.models import Order, OrderItem
from storage.models import (
    InventoryItem)
from users.models import CustomUser
from services.menu.menu import (
    check_if_items_can_be_made, update_ingredient_storage_on_cooking,

)





def create_order(
    user_id, total_price, items, in_an_institution, spent_bonus_points=0, pass_check_if_all_items_can_be_made=False, table_number=0
):
    with transaction.atomic():
        user = CustomUser.objects.get(id=user_id)
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            order_type="В заведении" if in_an_institution else "На вынос",
            branch=user.branch,
            bonuses_used=spent_bonus_points,
        )

        order_items = []
        for item in items:
            menu_item = Menu.objects.get(id=item["item_id"])
            if check_if_items_can_be_made(menu_item, user.branch.id, item["quantity"]):
                order_item = OrderItem(
                    order=order,
                    menu=menu_item,
                    menu_quantity=item["quantity"]
                )
                order_items.append(order_item)
                update_ingredient_storage_on_cooking(menu_item, user.branch, item["quantity"])
        if not pass_check_if_all_items_can_be_made and len(order_items) != len(items):
            return None
        OrderItem.objects.bulk_create(order_items)
        return order

def reorder(order_id):
    with transaction.atomic():
        old_order = Order.objects.get(id=order_id)
        items = [
            {"item_id": order_item.menu.id, "quantity": order_item.menu_quantity}
            for order_item in old_order.items.all()
        ]
        return create_order(
            user_id=old_order.user.id,
            total_price=old_order.total_price,
            items=items,
            in_an_institution=old_order.order_type == "В заведении",
            spent_bonus_points=old_order.bonuses_used,
            table_number=old_order.table.number if old_order.table else 0
        )


def add_item_to_order(order_id, item_id, quantity=1):
    with transaction.atomic():
        order = Order.objects.get(id=order_id)
        if order.status != "Новый":
            return None

        menu_item = Menu.objects.get(id=item_id)
        if check_if_items_can_be_made(menu_item, order.branch.id, quantity):
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menu=menu_item,
                defaults={'menu_quantity': 0}
            )
            order_item.menu_quantity += quantity
            order_item.save()
            update_ingredient_storage_on_cooking(menu_item, order.branch, quantity)
            return order
        else:
            return None

def remove_order_item(order_item_id):
    with transaction.atomic():
        order_item = OrderItem.objects.get(id=order_item_id)
        order = order_item.order
        if order.status != "Новый":
            return None

        if order_item.menu_quantity > 1:
            order_item.menu_quantity -= 1
            order_item.save()
            update_ingredient_storage_on_cooking(order_item.menu, order.branch, -1)  # Возвращаем ингредиенты на склад
        else:
            order_item.delete()

        return order

def get_order_items_names_and_quantities(order_items):
    order_items_names_and_quantities = []
    for order_item in order_items:
        order_items_names_and_quantities.append(
            {
                "name": order_item.menu.name,
                "quantity": order_item.menu_quantity,
            }
        )
    return order_items_names_and_quantities


def get_reorder_information(order_id):
    try:
        order = Order.objects.get(id=order_id)
        current_branch = order.branch
        order_items = OrderItem.objects.filter(order=order)

        not_available_items = []
        for order_item in order_items:
            if not check_if_items_can_be_made(order_item.menu, current_branch.id, order_item.menu_quantity):
                not_available_items.append(order_item.menu.name)

        if len(not_available_items) == len(order_items):
            return {
                "message": f"Заказать в заведении {current_branch.name}?",
                "details": "В данный момент недоступны все товары из заказа. Попробуйте позже.",
                "status": status.HTTP_400_BAD_REQUEST,
            }
        elif not_available_items:
            return {
                "message": f"Заказать в заведении {current_branch.name}?",
                "details": f'Некоторые товары недоступны: {", ".join(not_available_items)}.',
                "status": status.HTTP_200_OK,
            }
        else:
            return {
                "message": f"Заказать в заведении {current_branch.name}?",
                "details": "Все товары доступны.",
                "status": status.HTTP_200_OK,
            }
    except Exception as e:
        return {
            "message": "Ошибка сервера.",
            "details": str(e),
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


def return_item_ingredients_to_storage(menu_item_id, branch_id, quantity):
    try:
        menu_item = Menu.objects.get(id=menu_item_id)
        for ingredient in menu_item.ingredients.all():
            inventory_item = InventoryItem.objects.get(name=ingredient.name, branch=branch_id)
            inventory_item.quantity += ingredient.quantity * quantity
            inventory_item.save()
        return "Updated successfully."
    except Exception as e:
        raise e


def return_order_item_to_storage(order_item_id):
    with transaction.atomic():
        order_item = OrderItem.objects.get(id=order_item_id)
        return_item_ingredients_to_storage(order_item.menu.id, order_item.order.branch.id, order_item.menu_quantity)
        return "Updated successfully."


def return_to_storage(order_id):
    try:
        order_items = OrderItem.objects.filter(order_id=order_id)
        for order_item in order_items:
            return_order_item_to_storage(order_item.id)
        return "Returned successfully."
    except Exception as e:
        raise e
