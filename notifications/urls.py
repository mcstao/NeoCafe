from django.urls import path

from .views import NotificationCreateView, NotificationDeleteView

urlpatterns = [
    path('create/', NotificationCreateView.as_view(), name='create'),
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='delete'),
]