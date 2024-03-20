from django.urls import path
from .views import (
    CreateOrderView,
    UpdateOrderView,
    ReorderView,
    ReorderInformationView,
    RemoveOrderItemView,
    AddItemToOrderView,
    CreateCustomerOrderView,
    UpdateCustomerOrderView, OrderListView,
)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('update-order/<int:order_id>/', UpdateOrderView.as_view(), name='update-order'),
    path('reorder/', ReorderView.as_view(), name='reorder'),
    path('reorder-info/', ReorderInformationView.as_view(), name='reorder-info'),
    path('remove-order-item/', RemoveOrderItemView.as_view(), name='remove-order-item'),
    path('add-item-to-order/', AddItemToOrderView.as_view(), name='add-item-to-order'),
    path('create-customer-order/', CreateCustomerOrderView.as_view(), name='create-customer-order'),
    path('update-customer-order/<int:order_id>/', UpdateCustomerOrderView.as_view(), name='update-customer-order'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]
