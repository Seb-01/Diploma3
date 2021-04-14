from django.contrib.auth import get_user_model, password_validation
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth.models import BaseUserManager
from eshopapi.models import Contact
from eshopapi.serializers import ContactSerializer
from shops_n_goods.serializers import ShopSerializer

User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class AuthUserSerializer(serializers.ModelSerializer):
    # это означает, что данные метод отдельный будет поставлять
    # A method field in DRF is a read-only field whose value can be generated dynamically
    # through a method definition as get_<field_name>
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_admin', 'auth_token')
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser', 'is_admin')

    def get_auth_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key

# для заглушки при выборе сериализатора в зависимости от нужного действия
class EmptySerializer(serializers.Serializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        # We validate the email to check if it already exists
        if user:
            raise serializers.ValidationError("Email is already taken")
        # The normalize_email method of BaseUserManager prevents different sign-ups of case sensitive email domains
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        # To let you know, these validation methods must take the form validate_<field_name> for field-level validation.
        password_validation.validate_password(value)
        return value

class PasswordChangeSerializer(serializers.Serializer):
    """

    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password does not match')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value



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

    """
    Несмотря на то, что явным образом в модели User не определен поле shop, при связи один к одному неявно создается
    # свойство, которое называется по имени зависимой модели - Shop, которое указывает на связанный объект этой модели.
    # То есть в данном случае это свойство будет называться "shop":
    """
    # StringRelatedField may be used to represent the target of the relationship using its __str__ method.
    shop=serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ['id','company', 'username', 'email', 'position', 'is_staff', 'is_active', 'is_superuser',
                  'type', 'contacts', 'shop']
        read_only_fields = ('id',)