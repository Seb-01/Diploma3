from rest_framework import serializers
from eshopapi.models import User, Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact
        fields = ['id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment',
                  'phone']

class UserSerializer(serializers.ModelSerializer):
    """
    По дефолту сериализатор может создавать/обновлять данные.
    """
    # отдельно получаем данных из таблиц, которые ссылаются на User
    # read_only атрибут означает, что ContactSerializer поле будет использоваться только
    # для отображения дополнительных данных. Соотвественно при создании/обновлении User
    # контакты его никак не затрагиваются. Нужно только для просмотра User
    # Сериализатор только для чтения работает только путем передачи экземпляра в сериализатор и
    # отображения этого экземпляра.
    # many=True - означает, что у одного User может быть несколько контактов
    contacts=ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id','company', 'username', 'email', 'position', 'is_staff', 'is_active',
                  'type', 'contacts']



