from django.urls import path
from .views import CustomerProfileView, CustomerEditProfileView

urlpatterns = [
    path("profile/", CustomerProfileView.as_view() , name="customer-profile"),
    path("profile/edit/", CustomerEditProfileView.as_view(), name="customer-profile-edit"),
]
