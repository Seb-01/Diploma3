from rest_framework import serializers
import backend.settings
from eshopapi.models import Order, OrderItem

# сериализатор для позиции в заказе
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product_info', 'quantity')
        read_only_fields = ('id', 'order', 'product_info', 'quantity')

# Общий сериализатор
class OrderSerializer(serializers.ModelSerializer):
    # StringRelatedField may be used to represent the target of the relationship using its __str__ method.
    # Чтобы можно было видеть не просто ID, но как в User def __str__(self):
    #         return f'{self.first_name} {self.last_name} {self.email}'
    user = serializers.StringRelatedField()
    contact=serializers.StringRelatedField()
    # здесь мы выдаем список всех позиций в заказе:
    # Через related_name='ordered_items', определенный в OrderItem в атрибуте order, последний
    # получает доступ ко всем позициям в заказе
    positions = OrderItemSerializer(source='ordered_items', many=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'dt', 'state', 'contact', 'positions')
        read_only_fields = ('id','user', 'state', 'contact', 'positions')

# Сериализатор для создания заказа
class OrderCreateSerializer(serializers.ModelSerializer):
    # StringRelatedField may be used to represent the target of the relationship using its __str__ method.
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'dt')
        read_only_fields = ('id','user')


# Сериализатор для добавления позиции в заказ
class OrderAddItemSerializer(serializers.ModelSerializer):
    # StringRelatedField may be used to represent the target of the relationship using its __str__ method.
    user = serializers.StringRelatedField()
    id_product_info=serializers.IntegerField()
    quantity=serializers.IntegerField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'id_product_info', 'quantity')
        read_only_fields = ('id','user')