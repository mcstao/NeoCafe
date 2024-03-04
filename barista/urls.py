from django.urls import path
from .views import BaristaProfileView

urlpatterns = [
    path("profile/", BaristaProfileView.as_view() , name="barista-profile"),
]