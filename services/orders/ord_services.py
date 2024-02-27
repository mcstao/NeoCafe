import logging
from decimal import Decimal
from django.db.models import Sum
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class OrderService:
    @staticmethod
    def update_total_price(order):
        from orders.models import OrderItem  # Импорт локально внутри функции
        total_price = order.items.aggregate(
            total_price=Sum(models.F("menu__price") * models.F("menu_quantity"), output_field=models.DecimalField())
        )["total_price"] or Decimal("0.00")
        amount = order.total_price = total_price
        return max(amount - order.bonuses_used, Decimal("0.00"))

    @staticmethod
    def apply_bonuses(order, bonuses_amount):
        from orders.models import Order  # Импорт локально внутри функции
        logger.info(
            f"Начало применения бонусов: {bonuses_amount}, текущий баланс клиента: {order.user.bonus}"
        )
        if order.user.bonus < bonuses_amount:
            raise ValueError("Недостаточно бонусов")
        order.user.bonus -= bonuses_amount
        order.bonuses_used = bonuses_amount
        order.user.save()

        logger.info(f"Конец применения бонусов, новый баланс: {order.user.bonus}")

        total_cost = OrderService.update_total_price(order)
        return max(total_cost, Decimal("0.00"))

    @staticmethod
    def apply_cashback(order):
        from orders.models import Order  # Импорт локально внутри функции
        if order.status == "completed":
            total_price = OrderService.update_total_price(order)
            cashback = total_price * Decimal("0.05")
            if order.user and order.user.role == "client":
                order.user.bonus += cashback
                order.user.save()
            return cashback
        return Decimal("0.00")

    @staticmethod
    def set_in_process(order):
        from orders.models import Order  # Импорт локально внутри функции
        if order.status == "new":
            order.status = "in_process"
            order.save()
            return True
        return False

    @staticmethod
    def set_completed(order):
        from orders.models import Order  # Импорт локально внутри функции
        if order.status in ["new", "in_process"]:
            order.status = "completed"
            order.save()
            return True
        return False

    @staticmethod
    def set_cancelled(order):
        from orders.models import Order  # Импорт локально внутри функции
        if order.status not in ["completed", "cancelled"]:
            order.status = "cancelled"
            order.save()
            return True
        return False
