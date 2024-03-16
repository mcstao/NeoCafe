from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.customer.order import create_order, reorder, get_reorder_information, remove_order_item, add_item_to_order
# from administrator.permissions import IsClientUser
from .models import Order
from .serializers import OrderStaffSerializer

class CreateOrderView(APIView):
    """
    View for orders.
    """
    @extend_schema(
        request=OrderStaffSerializer,
        responses={201: OrderStaffSerializer},
        description="Creates an order for staff."
    )

    def post(self, request):
        """
        Creates order.
        """
        order = create_order(
            user_id=request.user.id,
            total_price=request.data["total_price"],
            items=request.data["items"],
            bonuses_used=request.data["bonuses_used"],
            is_dine_in=request.data["is_dine_in"],
            table_number=request.data["table_number"]
            if "table_number" in request.data
            else 0,
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
    """
    View for reordering.
    """


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
    """
    View for reorder information.
    """

    @extend_schema(
        responses={201: OrderStaffSerializer},
        methods=['GET'],
        description="Reorders an existing order.",
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
    """
    View for removing order item.
    """


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
    """
    View for adding item to order.
    """


    def post(self, request):
        """
        Adds item to order.
        """
        order_id = request.query_params["order_id"]
        item_id = request.query_params["item_id"]

        order = add_item_to_order(
            order_id=order_id,
            item_id=item_id,
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