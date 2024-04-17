from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'timestamp', 'status', 'recipient', 'table')
    fields = ('title', 'description', 'timestamp', 'status', 'recipient', 'read', 'table')
    readonly_fields = ('timestamp',)