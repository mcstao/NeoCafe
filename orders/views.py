from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from services.customer.order import create_order, reorder, get_reorder_information, remove_order_item, add_item_to_order


from .serializers import OrderStaffSerializer

class CreateOrderView(APIView):
    """
    View for orders.
    """
    @extend_schema(
        request=OrderStaffSerializer,
        responses={201: OrderStaffSerializer},
        description="Создает заказ"
    )

    def post(self, request):
        """
        Creates order.
        """
        order = create_order(
            user_id=request.user.id,
            items=request.data["items"],
            bonuses_used=request.data["bonuses_used"],
            order_type=request.data["order_type"],
            table_number=request.data.get("table_number", 0),
        )
        if order:
            return Response(
                OrderStaffSerializer(order).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Not enough stock.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReorderView(APIView):
    @extend_schema(
        responses={201: OrderStaffSerializer},
        description="Повторно создает заказ по его идентификатору.",
        request=inline_serializer(
            name='Reorder',
            fields={
                'order_id': serializers.IntegerField(),
            }
        )
    )


    def get(self, request):
        """
        Reorders order.
        """
        order = reorder(request.query_params["order_id"])
        if order:
            return Response(
                OrderStaffSerializer(order).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Извините, но в данный момент невозможно сделать заказ. Не хватает ингридиентов.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


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
                'order_item_id': serializers.IntegerField(),
            }
        ),

    )

    def delete(self, request):
        """
        Removes order item.
        """
        remove_order_item(request.query_params["order_item_id"])
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
            }
        ),
        responses={201: OrderStaffSerializer},
        description="Добавляет пункт в заказ."
    )
    def post(self, request):
        """
        Adds item to order.
        """
        order_id = request.query_params["order_id"]
        menu_id = request.query_params["menu_id"]

        order = add_item_to_order(
            order_id=order_id,
            menu_id=menu_id,
        )
        if order:
            return Response(
                OrderStaffSerializer(order).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Not enough stock.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )