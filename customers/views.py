from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions, generics, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branches.models import Branch
from customers.serializers import CustomerProfileSerializer, CustomerEditProfileSerializer, MenuSerializer, \
    MenuItemDetailSerializer, ChangeBranchSerializer, UserOrdersSerializer
from menu.models import Menu
from orders.models import Order
from orders.serializers import OrderSerializer
from services.menu.menu import get_popular_items, get_compatibles, item_search, \
    check_if_items_can_be_made
from services.users.permissions import IsCustomer, IsEmailVerified


class CustomerProfileView(generics.GenericAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsCustomer, IsEmailVerified]

    def get(self, request):
        user = request.user
        serializer = CustomerProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerEditProfileView(generics.GenericAPIView):
    permission_classes = [IsCustomer, IsEmailVerified]
    serializer_class = CustomerEditProfileSerializer

    def put(self, request):
        user = request.user
        first_name = request.data.get("first_name", user.first_name)
        birth_date = request.data.get("birth_date", user.birth_date)
        user.first_name = first_name
        user.birth_date = birth_date
        user.save()
        return Response(
            {"detail": "Профиль успешно изменен"}, status=status.HTTP_200_OK
        )


class MenuView(APIView):
    """
    View for getting menu items.
    """

    @extend_schema(
        summary="Get menu",
        description="Use this endpoint to get menu items.",
        responses={200: MenuSerializer},
    )
    def get(self, request, format=None):
        """
        Get menu items.
        """
        user = request.user
        category_id = request.GET.get("category_id")

        if category_id:
            items = Menu.objects.filter(branch=user.branch, category_id=category_id, available=True)
        else:
            items = Menu.objects.filter(branch=user.branch, available=True)

        serializer = MenuSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MenuItemDetailView(APIView):
    """
    View for getting menu item detail.
    """

    @extend_schema(
        summary="Получить детальную информацию о пункте меню",
        description="Используйте этот эндпоинт для получения детальной информации о пункте меню по ID.",
        responses={200: MenuItemDetailSerializer},
    )
    def get(self, request, item_id, format=None):
        """
        Get menu item detail.
        """
        try:
            item = Menu.objects.get(id=item_id)
        except Menu.DoesNotExist:
            return Response({"message": "Item does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PopularItemsView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get popular items",
        description="Use this endpoint to get popular items.",
        responses={200: MenuItemDetailSerializer(many=True)},
    )
    def get(self, request, format=None):
        """
        Get popular items.
        """
        user = request.user
        items = get_popular_items(user.branch_id)  # Убедитесь, что функция get_popular_items ожидает id филиала
        serializer = MenuItemDetailSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompatibleItemsView(APIView):
    """
    View for getting compatible menu items.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get compatible items",
        description="Use this endpoint to get menu items that are compatible with a given menu item.",
        responses={200: MenuItemDetailSerializer(many=True)},
    )
    def get(self, request, item_id, format=None):
        """
        Get compatible items.
        """
        branch_id = request.user.branch.id
        items = get_compatibles(item_id, False, branch_id)  # is_ready_made_product убран, так как у вас одна модель Menu
        serializer = MenuItemDetailSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ItemSearchView(APIView):
    """
    View to search items.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Search items.
        """
        user = request.user
        query = request.GET.get("query")
        items = item_search(query, user.branch.id)
        return Response(items, status=status.HTTP_200_OK)


class CheckIfItemCanBeMadeView(APIView):
    """
    View for checking if a menu item can be made.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Check if menu item can be made",
        description="Use this endpoint to check if a menu item can be made based on its availability and the stock of its ingredients.",
        responses={
            200: "Item can be made",
            400: "Item can't be made",
        },
        parameters=[
            OpenApiParameter("item_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Menu item id"),
            OpenApiParameter("quantity", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Quantity")
        ],
    )
    def post(self, request, format=None):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity", 1)  # Assume default quantity is 1 if not provided

        try:
            item = Menu.objects.get(id=item_id)
        except Menu.DoesNotExist:
            return Response({"message": "Menu item does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if check_if_items_can_be_made(item_id, request.user.branch.id, quantity):
            return Response({"message": "Item can be made."}, status=status.HTTP_200_OK)

        return Response({"message": "Item can't be made."}, status=status.HTTP_400_BAD_REQUEST)

class ChangeBranchView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeBranchSerializer

    @extend_schema(
        summary="Change branch",
        description="Use this endpoint to change branch. You need to provide branch id.",
        responses={200: "Branch changed successfully", 400: "Invalid data"},
    )
    def post(self, request, format=None):
        """
        Change branch.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            branch_id = serializer.validated_data.get("branch_id")
            user = request.user
            try:
                branch = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                return Response({"message": "Branch does not exist."}, status=status.HTTP_404_NOT_FOUND)

            user.branch = branch
            user.save()
            return Response({"message": "Branch changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyIdView(APIView):
    """
    View for getting user's id.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user's ID",
        description="Use this endpoint to get the authenticated user's ID.",
        responses={200: "User's ID"},
    )
    def get(self, request, format=None):
        """
        Get user's ID.
        """
        user = request.user
        return Response({"id": user.id}, status=status.HTTP_200_OK)

class MyOrdersView(APIView):
    """
    View for getting user's orders.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user's orders",
        description="Use this endpoint to get the authenticated user's orders.",
        responses={200: UserOrdersSerializer},
    )
    def get(self, request, format=None):
        """
        Get user's orders.
        """
        user = request.user
        serializer = UserOrdersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
class MyOrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    @extend_schema(
        summary="Get order detail",
        description="Use this endpoint to get details of a specific order by its ID.",
        responses={200: OrderSerializer},
    )

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)