from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework_yaml.parsers import YAMLParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
import backend.settings
from eshopapi.models import Shop
from eshopapi.permissions import MyIsAdminUser
from shops_n_goods.serializers import ShopSerializer, ShopPriceListSerializer
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
    #permission_classes = [MyIsAdminUser, ]

    """
    Сюда сложим все сериализаторы - каждый под свой конкретный @action
    """
    # общий  - по умолчанию
    serializer_class = ShopSerializer

    #parser_classes = (YAMLParser,)

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






