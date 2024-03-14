from branches.models import Branch
from orders.models import Order, OrderItem


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
    ).only("id", "branch__name", "branch__image", "created")
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

