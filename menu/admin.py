from django.contrib import admin

from menu.models import Menu, Category, ExtraItem

admin.site.register(Menu)
admin.site.register(Category)
admin.site.register(ExtraItem)