from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.customer.order import create_order, reorder, get_reorder_information, remove_order_item, \
    return_to_storage, return_item_ingredients_to_storage, remove_extra_products, return_extra_ingredients_to_storage, \
    create_order_waiter
from services.users.permissions import IsBarista, IsWaiter
from .models import Table, Order, OrderItem, OrderItemExtraProduct

from .serializers import OrderStaffSerializer, OrderCustomerSerializer, TableDetailSerializer, TableSerializer, \
    OrderDetailedListSerializer, OrderOneSerializer


class CreateOrderView(APIView):
    permission_classes = [IsBarista | IsWaiter]
    @extend_schema(request=OrderStaffSerializer, responses={201: OrderStaffSerializer}, description="Создает заказ")
    def post(self, request):
        waiter = request.user
        table = request.data.get("table")
        order_type = request.data.get("order_type")
        items = request.data.get("items", [])
        bonuses_used = request.data.get("bonuses_used", 0)

        table_id = None
        if table is not None:
            table = Table.objects.filter(table_number=table, branch=waiter.branch).first()
            if order_type == "В заведении" and (not table or not table.is_available):
                return Response({"message": "Table is not available or does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)
            table_id = table.id if table else None

        try:
            order = create_order_waiter(waiter.id, items, order_type, bonuses_used, table_id)
            return Response(OrderStaffSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateOrderView(APIView):
    serializer_class = OrderStaffSerializer
    permission_classes = [IsBarista | IsWaiter]

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
    permission_classes = [IsBarista | IsWaiter]
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
            return Response(
                {"message": "Извините, но в данный момент невозможно сделать заказ. Не хватает ингридиентов."},
                status=status.HTTP_400_BAD_REQUEST)


class ReorderInformationView(APIView):
    permission_classes = [IsBarista | IsWaiter]
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
    permission_classes = [IsAuthenticated]
    @extend_schema(
        responses={200: None},
        description="Удаляет пункт или обновляет количество в заказе.",
        request=inline_serializer(
            name='Removeorderitem',
            fields={
                'order_item_id': serializers.IntegerField(required=False),
                'quantity': serializers.IntegerField(required=False),
                'extra_product_id': serializers.IntegerField(required=False),
                'extra_quantity': serializers.IntegerField(required=False),
            }
        ),
    )
    def delete(self, request):
        order_item_id = request.data.get("order_item_id")
        quantity = request.data.get("quantity")
        extra_product_id = request.data.get("extra_product_id")
        extra_quantity = request.data.get("extra_quantity")

        if order_item_id:
            order_item = OrderItem.objects.filter(id=order_item_id).first()
            if not order_item:
                return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

            if quantity is not None:
                quantity = int(quantity)
            else:
                quantity = order_item.quantity

            remove_order_item(order_item_id, quantity)
            return_item_ingredients_to_storage(order_item.menu_id, order_item.order.branch_id, quantity)

        if extra_product_id:
            extra_product = OrderItemExtraProduct.objects.filter(id=extra_product_id).first()
            if not extra_product:
                return Response({"error": "Extra product not found."}, status=status.HTTP_404_NOT_FOUND)

            if extra_quantity is not None:
                extra_quantity = int(extra_quantity)
            else:
                extra_quantity = extra_product.quantity

            remove_extra_products(extra_product_id, extra_quantity)
            return_extra_ingredients_to_storage(extra_product.extra_product.id, extra_product.order_item.order.branch_id, extra_quantity)

        return Response({"message": "Requested items were removed/updated."}, status=status.HTTP_200_OK)

class CreateCustomerOrderView(APIView):
    permission_classes = [IsAuthenticated]
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

            return Response(OrderCustomerSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Order could not be created."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCustomerOrderView(APIView):
    serializer_class = OrderCustomerSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = Order.objects.get(id=order_id)

        serializer = OrderCustomerSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            updated_order = serializer.save()

            if updated_order.status == "Отменено" and order.table:
                return_to_storage(updated_order.id)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableDetailView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return super().get_object()

class TableListCreateView(generics.ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

class TableListByBranchView(generics.ListAPIView):
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        return Table.objects.filter(branch__id=branch_id)


class OrderDetailedListView(generics.ListAPIView):
    serializer_class = OrderDetailedListSerializer
    queryset = Order.objects.all().order_by('-created')
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user_branch = self.request.user.branch
        queryset = super().get_queryset().filter(branch=user_branch)

        status = self.request.query_params.get('status')
        order_type = self.request.query_params.get('order_type')

        if status:
            queryset = queryset.filter(status=status)

        if order_type:
            queryset = queryset.filter(order_type=order_type)

        if 'status__in' in self.request.query_params:
            status_in = self.request.query_params.get('status__in').split(',')
            queryset = queryset.filter(status__in=status_in)

        if 'order_type__in' in self.request.query_params:
            order_type_in = self.request.query_params.get('order_type__in').split(',')
            queryset = queryset.filter(order_type__in=order_type_in)

        return queryset

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderOneSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'