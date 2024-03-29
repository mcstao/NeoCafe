from django.urls import path, include
from rest_framework import routers
from .views import InventoryItemViewSet

router = routers.DefaultRouter()

router.register(r'', InventoryItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
