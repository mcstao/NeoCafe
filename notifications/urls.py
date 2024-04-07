from django.urls import path

from .views import NotificationDeleteView

urlpatterns = [
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='delete'),
]