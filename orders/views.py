from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from services.customer.order import create_order, reorder, get_reorder_information, remove_order_item, \
    add_item_to_order, return_to_storage
from .models import Table, Order

from .serializers import OrderStaffSerializer, OrderCustomerSerializer


class CreateOrderView(APIView):
    @extend_schema(request=OrderStaffSerializer, responses={201: OrderStaffSerializer}, description="Создает заказ")
    def post(self, request):
        user = request.user
        table_number = request.data.get("table_number")
        order_type = request.data.get("order_type")
        items = request.data.get("items", [])
        bonuses_used = request.data.get("bonuses_used", 0)

        # Проверка доступности стола
        if order_type == "В заведении" and table_number is not None:
            table = Table.objects.filter(table_number=table_number, branch=user.branch).first()
            if not table or not table.is_available:
                return Response({"message": "Table is not available."}, status=status.HTTP_400_BAD_REQUEST)

        # Создание заказа
        try:
            order = create_order(user.id, items, order_type, bonuses_used, table_number)
            return Response(OrderStaffSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UpdateOrderView(APIView):
    serializer_class = OrderStaffSerializer
    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            serializer = OrderStaffSerializer(order, data=request.data, partial=True)

            if serializer.is_valid():
                updated_order = serializer.save()

                # Обновление статуса стола и возврат ингредиентов на склад
                if updated_order.status in ["Отменено", "Завершено"]:
                    if updated_order.table:
                        updated_order.table.is_available = True
                        updated_order.table.save()

                    if updated_order.status == "Отменено":
                        return_to_storage(updated_order.id)

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)



class ReorderView(APIView):
    @extend_schema(
        responses={201: OrderStaffSerializer},
        description="Повторно создает заказ по его идентификатору.",
        request=inline_serializer(
            name='Reorder',
            fields={'order_id': serializers.IntegerField()},
        )
    )
    def get(self, request):
        order = reorder(request.query_params["order_id"])
        if order:
            return Response(OrderStaffSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Извините, но в данный момент невозможно сделать заказ. Не хватает ингридиентов."}, status=status.HTTP_400_BAD_REQUEST)


class ReorderInformationView(APIView):
    @extend_schema(
        responses={200: None},
        description="Предоставляет информацию для повторного заказа."
    )

    @extend_schema(
        responses={201: OrderStaffSerializer},
        methods=['GET'],
        description="Reorders an existing order.",
        request=inline_serializer(
            name='Reorderinfo',
            fields={

                'order_id': serializers.IntegerField(),
            }
        )
    )
    def get(self, request):
        """
        Gets reorder information.
        """
        reorder_information = get_reorder_information(request.query_params["order_id"])
        return Response(
            {
                "message": reorder_information["message"],
                "details": reorder_information["details"],
            },
            status=reorder_information["status"],
        )

class RemoveOrderItemView(APIView):
    @extend_schema(
        responses={200: None},
        description="Удаляет пункт из заказа.",
        request=inline_serializer(
            name='Removeorderitem',
            fields={
                'order_id': serializers.IntegerField(),
                'order_item_id': serializers.IntegerField(),
            }
        ),

    )

    def delete(self, request):
        """
        Removes order item.
        """
        order_id = request.data.get("order_id")
        order_item_id = request.data.get("order_item_id")
        remove_order_item(order_id, order_item_id)
        return Response(
            {
                "message": "Order item removed.",
            },
            status=status.HTTP_200_OK,
        )


class AddItemToOrderView(APIView):
    @extend_schema(
        request=inline_serializer(
            name='AddItemToOrderRequest',
            fields={
                'order_id': serializers.IntegerField(),
                'menu_id': serializers.IntegerField(),
                'quantity': serializers.IntegerField(),
            }
        ),
        responses={201: OrderStaffSerializer},
        description="Добавляет пункт в заказ."
    )
    def post(self, request):
        order_id = request.data["order_id"]
        menu_id = request.data["menu_id"]
        quantity = request.data["quantity"]

        try:
            order = add_item_to_order(order_id, menu_id, quantity)
            if order:
                return Response(OrderStaffSerializer(order).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Item could not be added or insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateCustomerOrderView(APIView):
    @extend_schema(
        request=OrderCustomerSerializer,
        responses={201: OrderCustomerSerializer},
        description="Создает заказ клиента"
    )
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"message": "Authentication is required."}, status=status.HTTP_401_UNAUTHORIZED)

        table_number = request.data.get("table_number")
        order_type = request.data.get("order_type")
        items = request.data.get("items", [])
        bonuses_used = min(request.data.get("bonuses_used", 0), user.bonus)


        order = create_order(user.id, items, order_type, bonuses_used, table_number)

        if order:
            # Вычитаем использованные бонусы и обновляем бонусы пользователя
            user.bonus -= bonuses_used
            user.save(update_fields=['bonus'])
            return Response(OrderCustomerSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Order could not be created."}, status=status.HTTP_400_BAD_REQUEST)

class UpdateCustomerOrderView(APIView):
    serializer_class = OrderCustomerSerializer
    def patch(self, request, order_id):
        order = Order.objects.get(id=order_id)
        if order.user != request.user:
            return Response({"message": "You can only update your orders."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderCustomerSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            updated_order = serializer.save()

            if updated_order.status == "Завершено" and order.status != "Завершено":
                updated_order.user.bonus -= updated_order.bonuses_used
                updated_order.user.bonus += updated_order.total_price  # Начисление бонусов
                updated_order.user.save()

            if updated_order.status == "Отменено" and order.table:
                return_to_storage(updated_order.id)  # Возврат ингредиентов на склад

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

