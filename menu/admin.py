from django.contrib import admin

from menu.models import Menu, Category, ExtraItem, Ingredient

admin.site.register(Menu)
admin.site.register(Category)
admin.site.register(ExtraItem)
admin.site.register(Ingredient)