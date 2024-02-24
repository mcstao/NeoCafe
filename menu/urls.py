from django.urls import path, include
from rest_framework import routers
from .views import MenuViewSet, ExtraItemViewSet, CategoryViewSet

router = routers.DefaultRouter()

router.register(r'menus', MenuViewSet)
router.register(r'extra-items', ExtraItemViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
