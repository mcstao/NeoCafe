from django.urls import path

from .views import NotificationDeleteView, NotificationAllDeleteView

urlpatterns = [
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='delete'),
    path('delete/all/', NotificationAllDeleteView.as_view(), name='delete-all')
]