from eshopapi.models import Contact
from rest_framework import serializers

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact
        fields = ['id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment',
                  'phone']






