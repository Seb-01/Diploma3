from rest_framework import serializers

import backend.settings
from eshopapi.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    # StringRelatedField may be used to represent the target of the relationship using its __str__ method.
    user = serializers.StringRelatedField()

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'user', 'state', 'price_list')
        read_only_fields = ('id','user')

class ShopPriceListSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Shop
        fields = ('id','price_list',)

    # здесь немного своего кода добавляем, чтобы проапдейтить переданный нам экземпляр Shop
    def update(self, instance, validated_data):
        if backend.settings.DEBUG:
            print (instance)
        # заменяемый файл нужно ... удалить
        if instance.price_list:
             instance.price_list.delete()
        # все стандартно: обновляем и сохраняем
        return super().update(instance, validated_data)


