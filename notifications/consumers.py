from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from loguru import logger
from .models import Notification
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

class ClientNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for sending notifications to barista.
    """

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user = await self.get_user(self.user_id)
        print(self.user)
        if self.user.position == 'Клиент':
            self.user_group_name = f"client-{self.user.id}"

            # Connect to user-specific group
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.get_notifications()

    @database_sync_to_async
    def get_user(self, user_id):
        return get_user_model().objects.get(id=user_id)

    async def disconnect(self, close_code):
        # Disconnect from group
        await self.channel_layer.group_discard(
            self.user_group_name, self.channel_name
        )

    async def get_notifications(self):
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(recipient=self.user.id, read=False).order_by('-timestamp')
        )
        notifications_list = []
        for notification in notifications:
            notification.timestamp = timezone.localtime(notification.timestamp)
            notifications_list.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "description": notification.description,
                    "timestamp": notification.timestamp.strftime("%H:%M"),
                }
            )
            notification.read = True
            await sync_to_async(notification.save, thread_sensitive=True)()
        await self.send(text_data=json.dumps({"notifications": notifications_list}))

    async def get_notifications_handler(self, event):
        logger.info("Getting notifications")
        logger.info(event)
        await self.get_notifications()

    async def receive(self, text_data):
        ...
        # text_data_json = json.loads(text_data)

    async def receive_get_notifications(self, event):
        await self.get_notifications()


class WaiterNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for sending notifications to barista.
    """

    async def connect(self):
        self.waiter_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.waiter = await self.get_user(self.waiter_id)
        print(self.waiter)
        if self.waiter.position == 'Официант':
            self.user_group_name = f"waiter-{self.waiter.id}"

            # Connect to user-specific group
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.get_notifications()

    @database_sync_to_async
    def get_user(self, waiter_id):
        return get_user_model().objects.get(id=waiter_id)


    async def disconnect(self, close_code):
        # Disconnect from group
        await self.channel_layer.group_discard(
            self.user_group_name, self.channel_name
        )

    async def get_notifications(self, event=None):
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(recipient=self.waiter, read=False).order_by('-timestamp')
        )
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "description": notification.description,
                    "timestamp": notification.timestamp.strftime("%H:%M"),
                    "table": notification.table
                }
            )
            notification.read = True
            await sync_to_async(notification.save, thread_sensitive=True)()
        await self.send(text_data=json.dumps({"notifications": notifications_list}))

    async def get_notifications_handler(self, event):
        logger.info("Getting notifications")
        logger.info(event)
        await self.get_notifications()

    async def receive(self, text_data):
        ...
        # text_data_json = json.loads(text_data)

    async def receive_get_notifications(self, event):
        await self.get_notifications()


class AdminNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for sending notifications to barista.
    """

    async def connect(self):
        self.admin_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.admin = await self.get_user(self.admin_id)
        print(self.admin)
        if self.admin.position == 'Админ':
            self.user_group_name = f"admin-{self.admin.id}"

            # Connect to user-specific group
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.get_notifications()

    @database_sync_to_async
    def get_user(self, admin_id):
        return get_user_model().objects.get(id=admin_id)


    async def disconnect(self, close_code):
        # Disconnect from group
        await self.channel_layer.group_discard(
            self.user_group_name, self.channel_name
        )

    async def get_notifications(self, event=None):
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(recipient=self.admin, read=False).order_by('-timestamp')
        )
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "description": notification.description,
                    "timestamp": notification.timestamp.strftime("%H:%M"),
                }
            )
            notification.read = True
            await sync_to_async(notification.save, thread_sensitive=True)()
        await self.send(text_data=json.dumps({"notifications": notifications_list}))

    async def get_notifications_handler(self, event):
        logger.info("Getting notifications")
        logger.info(event)
        await self.get_notifications()

    async def receive(self, text_data):
        ...
        # text_data_json = json.loads(text_data)

    async def receive_get_notifications(self, event):
        await self.get_notifications()


class BaristaNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for sending notifications to barista.
    """

    async def connect(self):
        self.barista_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.barista = await self.get_user(self.barista_id)
        print(self.barista)
        if self.barista.position == 'Бармен':
            self.user_group_name = f"barista-{self.barista.id}"

            # Connect to user-specific group
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.get_notifications()

    @database_sync_to_async
    def get_user(self, barista_id):
        return get_user_model().objects.get(id=barista_id)


    async def disconnect(self, close_code):
        # Disconnect from group
        await self.channel_layer.group_discard(
            self.user_group_name, self.channel_name
        )

    async def get_notifications(self, event=None):
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(recipient=self.barista, read=False).order_by('-timestamp')
        )
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "description": notification.description,
                    "timestamp": notification.timestamp.strftime("%H:%M"),
                    "table": notification.table
                }
            )
            notification.read = True
            await sync_to_async(notification.save, thread_sensitive=True)()
        await self.send(text_data=json.dumps({"notifications": notifications_list}))

    async def get_notifications_handler(self, event):
        logger.info("Getting notifications")
        logger.info(event)
        await self.get_notifications()

    async def receive(self, text_data):
        ...
        # text_data_json = json.loads(text_data)

    async def receive_get_notifications(self, event):
        await self.get_notifications()