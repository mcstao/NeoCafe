from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Neocafe24.settings")

app = Celery("Neocafe24")

# Используем строку URL для указания брокера (например, Redis)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Устанавливаем поведение повторного подключения при запуске
app.conf.broker_connection_retry_on_startup = True

# Автообнаружение задач во всех django-приложениях
app.autodiscover_tasks()

