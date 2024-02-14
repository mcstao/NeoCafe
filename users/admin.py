from django.contrib import admin
from .models import EmployeeSchedule, CustomUser



class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "branch",
        "position",
        "is_verified",
        "is_active",
        "is_staff",
        "bonus",
    )
    list_display_links = (
        "id",
        "first_name",
        "last_name",
        "email",
        "branch",
        "position",
        "is_verified",
        "is_active",
        "is_staff",
        "bonus",
    )
    list_filter = ("branch", "position", "is_verified", "is_active", "is_staff")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "branch",
        "position",
        "is_verified",
        "is_active",
        "is_staff",
        "bonus",
    )
    list_per_page = 25


admin.site.register(EmployeeSchedule)
admin.site.register(CustomUser, CustomUserAdmin)
