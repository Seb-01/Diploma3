from rest_framework import serializers
from eshopapi.models import Shop


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'user', 'state', 'price_list')
        read_only_fields = ('id',)

