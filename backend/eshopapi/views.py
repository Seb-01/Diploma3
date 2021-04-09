from rest_framework import viewsets

import backend.settings
from eshopapi.models import User
from eshopapi.serializers import UserSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    # добавим аутентификацию
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    if backend.settings.DEBUG == True:
        print(super().request.user)
        print(super().request.auth)

    # и авторизацию
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer