from django.urls import path
from .views import OrderCreateAPIView, OrderHistory

urlpatterns = [
    path('create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('history/', OrderHistory.as_view(), name='order-history'),
]
