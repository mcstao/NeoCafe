from django.urls import path
from .views import WaiterProfileView

urlpatterns = [
    path("profile/", WaiterProfileView.as_view(), name="waiter-profile"),
]