from django.urls import path
from .views import (
    CreateOrderView,
    UpdateOrderView,
    ReorderView,
    ReorderInformationView,
    RemoveOrderItemView,
    CreateCustomerOrderView,
    UpdateCustomerOrderView, TableDetailView, TableListByBranchView, TableListCreateView, OrderDetailedListView,
)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('update-order/<int:order_id>/', UpdateOrderView.as_view(), name='update-order'),
    path('reorder/', ReorderView.as_view(), name='reorder'),
    path('reorder-info/', ReorderInformationView.as_view(), name='reorder-info'),
    path('remove-order-item/', RemoveOrderItemView.as_view(), name='remove-order-item'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('create-customer-order/', CreateCustomerOrderView.as_view(), name='create-customer-order'),
    path('update-customer-order/<int:order_id>/', UpdateCustomerOrderView.as_view(), name='update-customer-order'),
    path('tables/branch/<int:branch_id>/', TableListByBranchView.as_view(), name='table-list-by-branch'),
    path('tables/', TableListCreateView.as_view(), name='table-list-create'),
    path('order-list/', OrderDetailedListView.as_view(), name='order-list'),
]
