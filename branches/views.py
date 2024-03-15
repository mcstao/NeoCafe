from rest_framework import viewsets
from rest_framework.response import Response
from storage.models import Branch, InventoryItem
from branches.serializers import BranchSerializer
from menu.serializers import MenuSerializer

from drf_spectacular.utils import extend_schema


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    @extend_schema(
        description="Get the menu items available at this branch with enough"
                    " ingredients and ready-made products in stock.",
        summary="Branch Menu Items",
        responses={200: MenuSerializer(many=True)}
    )
    def get_menu_items(self, request, *args, **kwargs):
        branch = self.get_object()
        menu_items = self.get_menu_items_with_enough_ingredients(branch)
        ready_products = self.get_ready_products(branch)
        # Добавляем готовые продукты только если их количество больше 0
        if ready_products.exists():
            menu_items.extend(ready_products)
        serializer = MenuSerializer(menu_items, many=True)
        return Response(serializer.data)

    def get_menu_items_with_enough_ingredients(self, branch):
        menu_items = branch.menu_items.all()
        available_menu_items = []
        for menu_item in menu_items:
            if self.menu_item_has_enough_ingredients(menu_item, branch):
                available_menu_items.append(menu_item)
        return available_menu_items

    def menu_item_has_enough_ingredients(self, menu_item, branch):
        for ingredient in menu_item.ingredients.all():
            try:
                stock = InventoryItem.objects.get(branch=branch, name=ingredient.name, category='Сырье')
            except InventoryItem.DoesNotExist:
                return False

            if stock.quantity < ingredient.quantity:
                return False

        return True

    def get_ready_products(self, branch):
        # Получаем все готовые продукты на складе филиала
        ready_products = InventoryItem.objects.filter(branch=branch, category='Готовые продукты', quantity__gt=0)
        return ready_products

