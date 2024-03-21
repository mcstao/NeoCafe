from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=InventoryItem.CATEGORY_CHOICES)
    arrival_date = serializers.DateField(input_formats=[
        '%d-%m-%Y',  # DD-MM-YYYY
        '%d.%m.%Y',  # DD.MM.YYYY
        '%Y-%m-%d',  # YYYY-MM-DD
        '%d/%m/%Y',  # DD/MM/YYYY
        '%m/%d/%Y',  # MM/DD/YYYY
        '%Y/%m/%d',  # YYYY/MM/DD
        '%b %d, %Y',  # Mar 22, 2024
        '%B %d, %Y',  # March 22, 2024
        '%d %b, %Y',  # 22 Mar, 2024
        '%d %B, %Y',  # 22 March, 2024
    ])

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'quantity', 'quantity_unit', 'limit', 'limit_unit', 'category',
                  'arrival_date', 'is_running_out', 'branch']

    def to_internal_value(self, data):
        quantity = data.get('quantity')
        quantity_unit = data.get('quantity_unit')

        if quantity_unit == 'kg':
            data['quantity'] = float(quantity) * 1000  # Конвертируем килограммы в граммы
        elif quantity_unit == 'l':
            data['quantity'] = float(quantity) * 1000  # Конвертируем литры в миллилитры

        return super().to_internal_value(data)
