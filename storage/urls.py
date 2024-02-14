from django.urls import path
from .views import (CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
                    ItemListCreateView, ItemRetrieveUpdateDestroyView)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    path('storage/', ItemListCreateView.as_view(), name='item-list-create'),
    path('storage/<int:pk>/', ItemRetrieveUpdateDestroyView.as_view(), name='item-detail'),
]
