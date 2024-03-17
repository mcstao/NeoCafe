from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import permissions, generics, status, serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branches.models import Branch
from customers.serializers import CustomerProfileSerializer, CustomerEditProfileSerializer, CustomerMenuSerializer, \
    MenuItemDetailSerializer, ChangeBranchSerializer, UserOrdersSerializer, CheckIfItemCanBeMadeSerializer, \
    OrderSerializer
from menu.models import Menu
from orders.models import Order
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




class MenuItemDetailView(APIView):

    @extend_schema(
        summary="Получить детальную информацию о пункте меню",
        description="Используйте этот эндпоинт для получения детальной информации о пункте меню по ID.",
        responses={200: MenuItemDetailSerializer},
    )
    def get(self, request, item_id, format=None):

        try:
            item = Menu.objects.get(id=item_id)
        except Menu.DoesNotExist:
            return Response({"message": "Item does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MenuItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularItemsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Самое популярное",
        description="Самое популярное",
        responses={200: MenuItemDetailSerializer(many=True)},
    )
    def get(self, request, format=None):
        user = request.user
        items = get_popular_items(user.branch_id)  # Убедитесь, что функция get_popular_items ожидает id филиала
        serializer = MenuItemDetailSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompatibleItemsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Рекомендации к заказу",
        description="Рекомендация",
        responses={200: MenuItemDetailSerializer(many=True)},
    )
    def get(self, request, item_id, format=None):
        branch_id = request.user.branch.id
        items = get_compatibles(item_id, branch_id)
        serializer = MenuItemDetailSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Поиск меню по филиалу",
        description="...",
        responses={
            200: inline_serializer(
                name='ItemSearchResponse',
                fields={
                    'items': serializers.ListField(
                        child=serializers.DictField(
                            child=serializers.CharField()
                        )
                    )
                }
            ),
        },
    )
    def get(self, request, format=None):
        user = request.user
        query = request.GET.get("query")
        items = item_search(query, user.branch.id)
        return Response(items, status=status.HTTP_200_OK)


class CheckIfItemCanBeMadeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверяет можно ли изготовить",
        description="Проверка на возможность изготовление чего-то",
        request=CheckIfItemCanBeMadeSerializer,
        responses={
            200: inline_serializer(
                name='ItemCanBeMadeResponse',
                fields={'message': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ItemCannotBeMadeResponse',
                fields={'message': serializers.CharField()}
            ),
        },
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
        description="Эндпоинт для смены филиала",
        responses={
            200: inline_serializer(
                name='ChangeBranchResponse200',
                fields={'message': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ChangeBranchResponse400',
                fields={'message': serializers.CharField()}
            ),
        },
    )
    def post(self, request, format=None):

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
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="ID пользователя",
        description="Выдает ID пользователя.",
        responses={
            200: inline_serializer(
                name='UserIdResponse',
                fields={'id': serializers.IntegerField()}
            ),
        },
    )
    def get(self, request, format=None):
        user = request.user
        return Response({"id": user.id}, status=status.HTTP_200_OK)


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Заказы пользователя",
        description="Заказы пользователя",
        responses={200: UserOrdersSerializer},
    )
    def get(self, request, format=None):
        user = request.user
        serializer = UserOrdersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyOrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    @extend_schema(
        summary="Детали заказа",
        description="Деталь заказа",
        responses={200: OrderSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
