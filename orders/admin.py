from django.contrib import admin

from orders.models import Order, OrderItem, Table, OrderItemExtraProduct

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Table)
admin.site.register(OrderItemExtraProduct)

