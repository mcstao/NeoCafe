from django.urls import re_path
from .consumers import ClientNotificationConsumer, WaiterNotificationConsumer, AdminNotificationConsumer

websocket_urlpatterns = [
    re_path(r'wss/client/(?P<user_id>\d+)/$', ClientNotificationConsumer.as_asgi()),
    re_path(r'wss/waiter/(?P<user_id>\d+)/$', WaiterNotificationConsumer.as_asgi()),
    re_path(r'wss/admin/(?P<user_id>\d+)/$', AdminNotificationConsumer.as_asgi()),
]