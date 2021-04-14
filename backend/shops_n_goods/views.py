from rest_framework import viewsets
from rest_framework_yaml.parsers import YAMLParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
import backend.settings
from eshopapi.models import Shop
from eshopapi.permissions import MyIsAdminUser
from shops_n_goods.serializers import ShopSerializer
from rest_framework import status

# Create your views here.

class ShopsViewSet(viewsets.ModelViewSet):
    """
    Допущены admin и менеджеры своих магазинов
    """
    # пока два варианта оставим
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    # здесь только через токен
    #authentication_classes = [TokenAuthentication, ]

    # и авторизацию + менеджер магазина авторизованный
    permission_classes = [MyIsAdminUser, ]

    #parser_classes = (YAMLParser,)

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


    # определим наши собственные действия для этого эндпойнта
    @action(detail=False, methods=['post'])
    def upload_price(self, request, filename, shop_id, format=None, *args, **kwargs):
        # получить имя файла нужно и проверить его
        # получить id магазина нужно и проверить его
        try:
            file = request.FILES['filename']
            # now upload to s3 bucket or your media file
        except Exception as e:
            if backend.settings.DEBUG == True:
                print (e)
            return Response(status,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Parsed data will be returned within the request object by accessing 'data' attr
        _data = request.data

        # ищем магазин и проверяем статус на активность
        # проверяем формат файла на корреткность
        # сохраяем файл
        return Response({'received data': request.data}, status=status.HTTP_201_CREATED)



