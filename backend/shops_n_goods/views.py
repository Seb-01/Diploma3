from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser,JSONParser
from rest_framework_yaml.parsers import YAMLParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
import backend.settings
from eshopapi.models import Shop
from eshopapi.permissions import MyIsAdminUser
from shops_n_goods.serializers import ShopSerializer, ShopPriceListSerializer
from rest_framework import status
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from yaml import load as load_yaml, Loader, safe_load_all, load_all

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
    #permission_classes = [MyIsAdminUser, ]

    """
    Сюда сложим все сериализаторы - каждый под свой конкретный @action
    """
    # общий  - по умолчанию
    serializer_class = ShopSerializer

    #parser_classes = (YAMLParser,)
    parser_classes = (JSONParser,)

    queryset = Shop.objects.all()

    # определим наши собственные действия для этого эндпойнта
    # почему put, а не post?
    # detail: boolean indicating if the current action is configured for a list or detail view.
    # я имею дело с конкретным магазином - "в который" направляю прайс-лист
    @action(methods=['PUT',], detail=True)
    def upload_price(self, request, *args, **kwargs):
        #
        #parser_classes = [MultiPartParser, FormParser, FileUploadParser]
        # по цепочке проверяется, пока не подойдет нужный анализатор
        parser_classes = [MultiPartParser, FormParser, FileUploadParser, YAMLParser]
        #
        file_serializer=ShopPriceListSerializer(data=request.data)

        # здесь разрешения должны быть размещены!
        if file_serializer.is_valid():
            shop=Shop.objects.get(id=kwargs['pk'])

            print(request.data.get('price_list'))
            print(request.data)

            file_serializer.update(shop, file_serializer.validated_data)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET', ], detail=True)
    def apply_price(self, request, *args, **kwargs):
        """
        разбираем прайс-лист от магазина
        """
        shop = Shop.objects.get(id=kwargs['pk'])
        #проверка: загружен ли прайс-лист
        if shop.price_list:
            print('Разбираем прайс лист!')


            # Вариант 1
            # открываем файл
            validate_url = URLValidator()
            # получаем адрес вида: http://127.0.0.1:8000/media/Svayznoy/price2.yaml
            price_URL='http://' + request.get_host()+backend.settings.MEDIA_URL+str(shop.price_list)
            print(price_URL)
            try:
                validate_url(price_URL)
            except ValidationError as e:
                return Response({'Error': str(e)}, status=status.HTTP_417_EXPECTATION_FAILED)
            else:
                # запрашиваем полезную инфо  - payload - по этому адресу: там наш файл!)
                stream = get(price_URL).content
                #stream = get(price_URL).text

                data = load_yaml(stream, Loader=Loader)
                print(data)
                #data = safe_load_all(stream)
                # 1. Проверка на магазин и менеджера:
                # name = data['shop'], user_id = request.user.id
                if data['shop'] != shop.name:
                    return Response({'Error': 'Invalide shop name in price!'},
                                    status=status.HTTP_417_EXPECTATION_FAILED)

            #Вариант 2
            """
            stream2 = str(backend.settings.MEDIA_ROOT) + '/' + str(shop.price_list)
            with open(stream2) as yaml_file:
                data = load_yaml(yaml_file, Loader=Loader)
                print(data)
            if data['shop'] != shop.name:
                return Response({'Error': 'Invalide shop name in price!'}, status=status.HTTP_417_EXPECTATION_FAILED)
            """


            return Response({'Status': 'Price is applying!'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Price in required'}, status=status.HTTP_428_PRECONDITION_REQUIRED)



