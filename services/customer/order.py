from django.db import transaction
from rest_framework import status

from branches.models import Branch
from menu.models import Menu
from orders.models import Order, OrderItem
from services.menu.menu import update_ingredient_storage_on_cooking, check_if_items_can_be_made
from storage.models import InventoryItem
from users.models import CustomUser


def get_branch_name_and_id_list():
    branches = Branch.objects.all().only("id", "name")
    return branches


def get_my_orders_data(user, statuses):
    """
    Get orders of the user based on their status.
    """
    orders = Order.objects.filter(
        user=user,
        status__in=statuses,
    ).only("id", "branch__name", "branch__image", "created", "is_dine_in", "table")
    return orders


def get_my_opened_orders_data(user):
    return get_my_orders_data(user, ["Новый", "В процессе"])


def get_my_closed_orders_data(user):
    return get_my_orders_data(user, ["Готово", "Отменено", "Завершено"])

def get_specific_order_data(order_id):
    """
    Get specific order data.
    """
    order = Order.objects.filter(id=order_id).select_related("branch").first()

    items = OrderItem.objects.filter(order=order).select_related("menu", "menu__category")

    data = {
        "order_id": order_id,
        "branch_name": order.branch.name,
        "order_date": order.created.strftime("%d.%m.%Y"),
        "items": [],
        "order_total_price": order.total_price,
        "order_bonuses_used": order.bonuses_used,
        "table_number": order.table,
        "is_dine_in": order.is_dine_in,
    }

    for item in items:
        data["items"].append({
            "item_name": item.menu.name,
            "item_price": item.menu.price,
            "item_quantity": item.menu_quantity,
            "item_total_price": item.menu.price * item.menu_quantity,
            "item_image": item.menu.image.url if item.menu.image else None,
            "item_id": item.menu.id,
            "item_category": item.menu.category.name,
        })

    return data


@transaction.atomic
def create_order(user_id, items, is_dine_in, spent_bonus_points=0, table_number=0):
    user = CustomUser.objects.get(id=user_id)
    total_price = 0  # Инициализация общей стоимости заказа

    # Создаем заказ с временной общей стоимостью, которую потом обновим
    order = Order.objects.create(
        user=user,
        total_price=0,  # временное значение
        bonuses_used=spent_bonus_points,
        is_dine_in=is_dine_in,
        branch=user.branch,
        table=table_number,
    )

    # Добавляем позиции заказа и считаем общую стоимость
    for item in items:
        menu_item = Menu.objects.get(id=item['menu_id'])
        if check_if_items_can_be_made(menu_item.id, order.branch.id, item['quantity']):
            OrderItem.objects.create(
                order=order,
                menu=menu_item,
                menu_quantity=item['quantity'],
            )
            total_price += menu_item.price * item['quantity']  # Увеличиваем общую стоимость
            update_ingredient_storage_on_cooking(menu_item.id, order.branch.id, item['quantity'])

    # Обновляем общую стоимость заказа
    order.total_price = total_price
    order.save()

    return order


def reorder(order_id):
    original_order = Order.objects.get(id=order_id)
    new_order = Order.objects.create(
        user=original_order.user,
        bonuses_used=original_order.bonuses_used,
        branch=original_order.branch,
        table=original_order.table,
        is_dine_in=original_order.is_dine_in
    )

    total_price = 0
    for item in original_order.items.all():
        if check_if_items_can_be_made(item.menu.id, original_order.branch.id, item.menu_quantity):
            OrderItem.objects.create(
                order=new_order,
                menu=item.menu,
                menu_quantity=item.menu_quantity,
            )
            total_price += item.menu.price * item.menu_quantity
            update_ingredient_storage_on_cooking(item.menu.id, original_order.branch.id, item.menu_quantity)

    new_order.total_price = total_price
    new_order.save()

    return new_order


@transaction.atomic
def add_item_to_order(order_id, menu_id, quantity):
    order = Order.objects.get(id=order_id)
    menu_item = Menu.objects.get(id=menu_id)

    if check_if_items_can_be_made(menu_id, order.branch.id, quantity):
        OrderItem.objects.create(
            order=order,
            menu=menu_item,
            menu_quantity=quantity,
        )
        order.total_price += menu_item.price * quantity
        update_ingredient_storage_on_cooking(menu_id, order.branch.id, quantity)


@transaction.atomic
def remove_order_item(order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)
    order = order_item.order

    if order.status == "Новый":
        order.total_price -= order_item.menu.price * order_item.menu_quantity
        order.save()
        order_item.delete()


"""get"""

def get_order_items_names_and_quantities(order_items):
    order_items_names_and_quantities = []
    for order_item in order_items:
        order_items_names_and_quantities.append({
            "name": order_item.menu.name,
            "quantity": order_item.menu_quantity,
        })
    return order_items_names_and_quantities


def get_reorder_information(order_id):
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        not_available_items = [item.menu.name for item in order_items if not item.menu.available]

        if not_available_items:
            message = "Некоторые товары недоступны."
        else:
            message = "Все товары доступны."

        return {
            "message": f"Заказать в заведении {order.branch.name}?",
            "details": message,
            "status": status.HTTP_200_OK if not not_available_items else status.HTTP_400_BAD_REQUEST,
        }
    except Order.DoesNotExist:
        return {
            "message": "Заказ не найден.",
            "details": "Заказ не найден.",
            "status": status.HTTP_404_NOT_FOUND,
        }



def return_item_ingredients_to_storage(menu_id, branch_id, quantity):
    try:
        menu_item = Menu.objects.get(id=menu_id)
        for ingredient in menu_item.ingredients.all():
            inventory_item = InventoryItem.objects.get(name=ingredient.name, branch=branch_id)
            inventory_item.quantity += ingredient.quantity * quantity
            inventory_item.save()
        return "Updated successfully."
    except Exception as e:
        raise e



def return_to_storage(order_id):
    try:
        order_items = OrderItem.objects.filter(order_id=order_id)
        for order_item in order_items:
            # Для каждого элемента заказа возвращаем его ингредиенты на склад
            for ingredient in order_item.menu.ingredients.all():
                inventory_item = InventoryItem.objects.get(name=ingredient.name, branch_id=order_item.order.branch.id)
                # Возвращаем количество использованных ингредиентов обратно на склад
                inventory_item.quantity += ingredient.quantity * order_item.menu_quantity
                inventory_item.save()
        return "Returned successfully."
    except Exception as e:
        raise e
