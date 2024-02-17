from django.urls import path
from .views import (CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
                    ItemListCreateView, ItemRetrieveUpdateDestroyView)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    path('', ItemListCreateView.as_view(), name='item-list-create'),
    path('<int:pk>/', ItemRetrieveUpdateDestroyView.as_view(), name='item-detail'),
]
