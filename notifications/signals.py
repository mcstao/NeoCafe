import time

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from loguru import logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from menu.models import Menu
from branches.models import Branch
from storage.models import InventoryItem
from orders.models import Order
from users.models import CustomUser
from .models import Notification
import loguru



User = get_user_model()


@receiver(post_save, sender=Notification)
def notify_clients(sender, instance, **kwargs):
    """
    Updates notifications on barista side.
    """
    logger.info("Updating notifications")
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
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "branch",
        {
            "type": "get_notifications",
        },
    )


@receiver(post_save, sender=Order, dispatch_uid="order_client_status_changed")
def client_status_changed(sender, instance, created, **kwargs):

    item_descriptions = [f"{item.menu.name} x {item.quantity}" for item in instance.items.all()]
    items_detail = ", ".join(item_descriptions)

    title = ""
    description = ""

    if instance.status == 'Новый':
        title = f"Ваш заказ оформлен"
        description = f"{items_detail}"
    elif instance.status == 'Готово':
        title = f"Ваш заказ готов"
        description = f"{items_detail}"
    elif instance.status == 'Завершено':
        title = f"Вы закрыли счет"
        description = f"{items_detail}"

    if title and description and instance.user:
        Notification.objects.create(
            title=title,
            description=description,
            recipient=instance.user,
            status=instance.status
        )

        user_name = f"client-{instance.user.id}"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_name,
            {
                "type": "get_notifications_handler",
            }
        )


@receiver(post_save, sender=Order, dispatch_uid="order_waiter_status_changed")
def waiter_status_changed(sender, instance, created, **kwargs):
    logger.info(f"Signal received for order with id {instance.id}. Created: {created}")

    item_descriptions = [f"{item.menu.name} x {item.quantity}" for item in instance.items.all()]
    items_detail = ", ".join(item_descriptions)
    table_number = ""
    title = ""
    description = ""

    if instance.status == 'Новый':
        title = f"Ваш заказ оформлен"
        description = f"{items_detail} {instance.table}"
        table_number = f"{instance.table}"
    elif instance.status == 'Готово':
        title = f"Заказ готов"
        description = f"{items_detail}"
        table_number = f"{instance.table}"
    elif instance.status == 'В процессе':
        title = f"Бариста принял заказ"
        description = f"{items_detail}"
    elif instance.status == 'Завершено':
        title = f"Закрытие счета"
        description = f"{items_detail}"
        table_number = f"{instance.table}"

    if title and description and table_number and instance.waiter:
        Notification.objects.create(
            title=title,
            description=description,
            table=table_number,
            recipient=instance.waiter,
            status=instance.status,
        )

        waiter_name = f"waiter-{instance.waiter.id}"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            waiter_name,
            {
                "type": "get_notifications_handler",
            }
        )


admins = User.objects.filter(position="Админ")


@receiver(post_save, sender=InventoryItem, dispatch_uid="storage_warning")
def storage_item_check(sender, instance, created, **kwargs):
    if instance.quantity <= instance.limit:

        for admin in admins:
            Notification.objects.create(
                title=f"Товар \"{instance.name}\" заканчивается",
                description=f"Количество на складе: {instance.quantity} {instance.quantity_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_save, sender=Branch, dispatch_uid="branch_created")
def branch_notification(sender, instance, created, **kwargs):
    if created:
        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новый филиал\"{instance.name}\"",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=Branch, dispatch_uid="branch_deleted")
def branch_deleted_notification(sender, instance, **kwargs):
    for admin in admins:
        Notification.objects.create(
            title=f"Удалили филиал\"{instance.name}\"",
            recipient=admin,
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"admin-{admin.id}",
            {
                "type": "get_notifications_handler",
            }
        )


@receiver(post_save, sender=InventoryItem, dispatch_uid="storage_created")
def storage_item_created(sender, instance, created, **kwargs):
    if created and instance.category == "Сырье":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новое сырье \"{instance.name}\" ",
                description=f"Количество на складе: {instance.quantity} {instance.quantity_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=InventoryItem, dispatch_uid="storage_deleted")
def storage_item_deleted(sender, instance, **kwargs):
    if instance.category == "Сырье":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили сырье \"{instance.name}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_save, sender=Menu, dispatch_uid="menu_created")
def menu_item_created(sender, instance, created, **kwargs):
    if created:

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новую позицию\"{instance.name}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=Menu, dispatch_uid="menu_deleted")
def menu_item_deleted(sender, instance, **kwargs):
    for admin in admins:
        Notification.objects.create(
            title=f"Удалили позицию\"{instance.name}\" ",
            recipient=admin,
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"admin-{admin.id}",
            {
                "type": "get_notifications_handler",
            }
        )


@receiver(post_save, sender=InventoryItem, dispatch_uid="storage_ready_created")
def storage_ready_created(sender, instance, created, **kwargs):
    if created and instance.category == "Готовые продукты":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новую готовую продукцию \"{instance.name}\" ",
                description=f"Количество на складе: {instance.quantity} {instance.quantity_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=InventoryItem, dispatch_uid="storage_ready_deleted")
def storage_ready_deleted(sender, instance, **kwargs):
    if instance.category == "Готовые продукты":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили готовую продукцию \"{instance.name}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_save, sender=CustomUser, dispatch_uid="staff_created")
def staff_created(sender, instance, created, **kwargs):
    if created and instance.position == "Официант" or "Бармен":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили {instance.first_name} как {instance.position}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=CustomUser, dispatch_uid="staff_deleted")
def staff_deleted(sender, instance, **kwargs):
    if instance.position == "Официант" or "Бармен":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили {instance.first_name} как {instance.position}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


baristas = User.objects.filter(position="Бармен")


@receiver(post_save, sender=Order, dispatch_uid="order_barista_status_accept")
def barista_status_accept(sender, instance, created, **kwargs):
    logger.info(f"Signal received for order with id {instance.id}. Created: {created}")

    item_descriptions = [f"{item.menu.name} x {item.quantity}" for item in instance.items.all()]
    items_detail = ", ".join(item_descriptions)
    table_number = ""
    title = ""
    description = ""

    if instance.status == 'Новый':
        for barista in baristas:
            if barista.branch == instance.branch:
                if instance.order_type == 'На вынос':
                    title = f"{instance.order_type} {instance.id}"
                    description = f"{items_detail}"
                elif instance.order_type == 'В заведении':
                    title = f"{instance.order_type} {instance.id}"
                    description = f"{items_detail}"
                    table_number = f"{instance.table}"

            if title and description and instance.waiter:
                Notification.objects.create(
                    title=title,
                    description=description,
                    recipient=barista,
                    status=instance.status,
                    table=table_number
                )

            barista_name = f"barista-{barista.id}"

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                barista_name,
                {
                    "type": "get_notifications_handler",
                }
            )
