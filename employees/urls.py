from django.urls import path
from .views import StaffCreateView, StaffDetailView, StaffByBranchView

urlpatterns = [
    path("staff/create/", StaffCreateView.as_view(), name="staff-create"),
    path("staff/list/", StaffByBranchView.as_view(), name="staff-list"),
    path("staff/<int:id>/", StaffDetailView.as_view(), name="employee-detail"),

]
