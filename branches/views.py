from rest_framework import generics, viewsets

from branches.serializers import BranchSerializer
from menu.serializers import MenuSerializer
from branches.models import Branch
from menu.models import Menu
from storage.models import InventoryItem
from drf_spectacular.utils import extend_schema


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchMenuView(generics.ListAPIView):
    serializer_class = MenuSerializer

    def get_queryset(self):
        user = self.request.user
        branch = user.branch

        menu_items = Menu.objects.all()
        available_menu_items = [
            menu_item for menu_item in menu_items if self.menu_item_has_enough_ingredients(menu_item, branch)
        ]

        return available_menu_items

    def menu_item_has_enough_ingredients(self, menu_item, branch):
        for ingredient in menu_item.ingredients.all():
            try:
                inventory_item = InventoryItem.objects.get(branch=branch, name=ingredient.name)
            except InventoryItem.DoesNotExist:
                return False
            if inventory_item.quantity < ingredient.quantity:
                return False
        return True

@extend_schema(
    description="Get a list of menu items in a branch filtered by category.",
    summary="Branch Menu Items by Category",
    responses={200: MenuSerializer(many=True)}
)
class BranchMenuByCategoryView(generics.ListAPIView):
    serializer_class = MenuSerializer

    def get_queryset(self):
        user = self.request.user
        branch = user.branch
        category_id = self.kwargs.get('category_id')


        menu_items = Menu.objects.filter(category__id=category_id)
        available_menu_items = [
            menu_item for menu_item in menu_items if self.menu_item_has_enough_ingredients(menu_item, branch)
        ]

        return available_menu_items

    def menu_item_has_enough_ingredients(self, menu_item, branch):
        for ingredient in menu_item.ingredients.all():
            try:
                inventory_item = InventoryItem.objects.get(branch=branch, name=ingredient.name)
            except InventoryItem.DoesNotExist:
                return False
            if inventory_item.quantity < ingredient.quantity:
                return False
        return True
