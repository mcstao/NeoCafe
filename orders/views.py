from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

# from administrator.permissions import IsClientUser
from .models import Order
from .serializers import OrderSerializer, OrderHistorySerializer


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    # permission_classes = [IsClientUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderHistory(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    # permission_classes = [IsClientUser]

    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)