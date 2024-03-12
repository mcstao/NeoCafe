from django.urls import path
from .views import (
    CustomerProfileView,
    CustomerEditProfileView,
    MenuView,
    MenuItemDetailView,
    PopularItemsView,
    CompatibleItemsView,
    ItemSearchView,
    CheckIfItemCanBeMadeView,
    ChangeBranchView,
    MyIdView,
    MyOrdersView,
    MyOrderDetailView
)

urlpatterns = [
    path("profile/", CustomerProfileView.as_view(), name="customer-profile"),
    path("profile/edit/", CustomerEditProfileView.as_view(), name="customer-profile-edit"),
    path("menu/", MenuView.as_view(), name='customer-menu'),
    path("menu/<int:item_id>/", MenuItemDetailView.as_view(), name="menu-item-detail"),
    path("popular-items/", PopularItemsView.as_view(), name="popular-items"),
    path("compatible-items/<int:item_id>/", CompatibleItemsView.as_view(), name="compatible-items"),
    path("search/", ItemSearchView.as_view(), name="item-search"),
    path("check-item/", CheckIfItemCanBeMadeView.as_view(), name="check-item"),
    path("change-branch/", ChangeBranchView.as_view(), name="change-branch"),
    path("my-id/", MyIdView.as_view(), name="my-id"),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("orders/<int:pk>/", MyOrderDetailView.as_view(), name="order-detail"),
]

