from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'timestamp', 'status', 'recipient')
    fields = ('title', 'description', 'timestamp', 'status', 'recipient', 'read')
    readonly_fields = ('timestamp',)