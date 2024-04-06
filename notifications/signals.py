import time

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from loguru import logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from orders.models import Order
from .models import Notification


SLEEP_TIME = 3


@receiver(post_save, sender=Notification)
def notify_clients(sender, instance, **kwargs):
    """
    Updates notifications on barista side.
    """
    logger.info("Updating notifications")
    time.sleep(SLEEP_TIME)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "branch",
        {
            "type": "get_notifications",
        },
    )
    logger.info("Updating notifications")


@receiver(post_delete, sender=Notification)
def notify_clients_on_delete(sender, instance, **kwargs):
    logger.info("Updating notifications")
    time.sleep(SLEEP_TIME)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "branch",
        {
            "type": "get_notifications",
        },
    )

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):

    item_descriptions = [f"{item.menu.name} x {item.quantity}" for item in instance.items.all()]
    items_detail = ", ".join(item_descriptions)

    title = ""
    description = ""

    if instance.status == 'Новый':
        title = f"Ваш заказ оформлен"
        description = f"{items_detail}"
    elif instance.status == 'Готов':
        title = f"Ваш заказ готов"
        description = f"{items_detail}"
    elif instance.status == 'Завершено':
        title = f"Вы закрыли счет"
        description = f"{items_detail}"

    if title and description:
        Notification.objects.create(
            title=title,
            description=description,
            recipient=instance.user,
            status=instance.status
        )

        user_name = f"client-{instance.user.id}"

        # Получаем слой каналов и отправляем сообщение
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_name,
            {
                "type": "get_notifications_handler",
            }
        )