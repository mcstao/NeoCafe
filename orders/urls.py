from django.urls import path
from .views import (
    CreateOrderView,
    ReorderView,
    ReorderInformationView,
    RemoveOrderItemView,
    AddItemToOrderView,
)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create_order'),
    path('reorder/', ReorderView.as_view(), name='reorder'),
    path('reorder-information/', ReorderInformationView.as_view(), name='reorder_information'),
    path('remove-order-item/', RemoveOrderItemView.as_view(), name='remove_order_item'),
    path('add-item-to-order/', AddItemToOrderView.as_view(), name='add_item_to_order'),
]
