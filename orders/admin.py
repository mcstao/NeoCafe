from django.contrib import admin

from orders.models import Order, OrderItem, Table

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Table)

