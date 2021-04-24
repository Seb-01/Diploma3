from django.shortcuts import render
from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from eshopapi.permissions import MyIsAdminUser
from users import serializers
from users.serializers import UserSerializer
from users.utils import get_and_authenticate_user, create_user_account

# Create your views here.

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    # добавим аутентификацию
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    # здесь только через токен
    # authentication_classes = [TokenAuthentication, ]

    # и авторизацию
    permission_classes = [MyIsAdminUser, ]

    queryset = User.objects.all()
    serializer_class = UserSerializer

"""
ViewSet actions

The default routers included with REST framework will provide routes for a standard set of
create/retrieve/update/destroy style actions

"""

class AuthViewSet(viewsets.ModelViewSet):
    # любой желающий может выполнять функции входа в систему
    permission_classes = [AllowAny, ]
    # заглушка,
    serializer_class = serializers.EmptySerializer
    # This will help us in fetching serializer classes based on the action. For our login action, we have defined
    # the ‘login’ as key and its serializer class as the key’s value.
    serializer_classes = {
        'login': serializers.UserLoginSerializer,
        'register': serializers.UserRegisterSerializer,
    }

    queryset = User.objects.all()

    #определим наши собственные действия для этого эндпойнта
    @action(methods=['POST', ], detail=False)
    def login(self, request):
        #получить сериализатор
        serializer = self.get_serializer(data=request.data)
        # проверка данных
        serializer.is_valid(raise_exception=True)
        # пользователя возвращаем с его креденшилами
        user = get_and_authenticate_user(**serializer.validated_data)
        # получаем токен
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    # используется внутри get_serializer
    # You may want to override this if you need to provide different
    # serializations depending on the incoming request.
    def get_serializer_class(self):
        # это словарь?
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        # логин есть среди action?
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        # если действие не определено в serializer_classes, то обработчик вернется к использованию
        # значения атрибута serializer_class - serializers.EmptySerializer по умолчанию
        return super().get_serializer_class()


    @action(methods=['POST', ], detail=False)
    def register(self, request):
        """
        create the register endpoint in views.py
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        """
        For logout, we actually don’t want anything in the request. Hence there is no need for serializer
         in case of logout. We can simply define the action for logout
        """
        # from django.contrib.auth import logout
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
    def password_change(self, request):
        """
        The new_password is validated via validate_password method which was also used for register endpoint.
        The password_change endpoint has the IsAuthenticated permission class defined on it as
        the user must be authenticated before accessing this endpoint
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

