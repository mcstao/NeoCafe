from django.contrib import admin

from menu.models import Menu, Category, ExtraItem, Ingredient, MenuItemIngredient

admin.site.register(Menu)
admin.site.register(Category)
admin.site.register(ExtraItem)
admin.site.register(Ingredient)
admin.site.register(MenuItemIngredient)