from django.urls import path, include
from rest_framework import routers
from .views import MenuViewSet, ExtraItemViewSet

router = routers.DefaultRouter()

router.register(r'', MenuViewSet)
router.register(r'extraitems', ExtraItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
