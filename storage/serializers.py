from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=InventoryItem.CATEGORY_CHOICES)

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'quantity', 'quantity_unit', 'limit', 'category',
                  'arrival_date', 'is_running_out', 'branch']

    def to_internal_value(self, data):
        quantity = data.get('quantity')
        quantity_unit = data.get('quantity_unit')

        if quantity_unit == 'kg':
            data['quantity'] = quantity * 1000  # Конвертируем килограммы в граммы
        elif quantity_unit == 'l':
            data['quantity'] = quantity * 1000  # Конвертируем литры в миллилитры

        return super().to_internal_value(data)

