from rest_framework import viewsets, status
from rest_framework.response import Response
from storage.models import InventoryItem
from storage.serializers import InventoryItemSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Пытаемся найти существующий элемент на складе с такими же атрибутами
        inventory_item = InventoryItem.objects.filter(
            branch=serializer.validated_data['branch'],
            name=serializer.validated_data['name'],
        ).first()

        if inventory_item:
            # Если такой элемент найден, обновляем его данные
            inventory_item.quantity += serializer.validated_data['quantity']
            inventory_item.save()
            return Response(self.get_serializer(inventory_item).data, status=status.HTTP_200_OK)
        else:
            # Если элемент не найден, создаем новый
            return super().create(request, *args, **kwargs)
