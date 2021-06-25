from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser,JSONParser
from rest_framework_yaml.parsers import YAMLParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
import backend.settings
from eshopapi.models import Shop, Category, Product, ProductInfo, Parameter
from eshopapi.permissions import MyIsAdminUser
from shops_n_goods.serializers import ShopSerializer, ShopPriceListSerializer
from rest_framework import status
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from yaml import load as load_yaml, Loader, safe_load_all, load_all
from django.db.models import F
import datetime

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
    #parser_classes = (MultiPartParser, FormParser, FileUploadParser, YAMLParser,)
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    queryset = Shop.objects.all()

    # определим наши собственные действия для этого эндпойнта
    # почему put, а не post? если создаются новые данные без удаления старых, то лучше put или patch
    # detail: boolean indicating if the current action is configured for a list or detail view.
    # а я имею дело с конкретным магазином - "в который" направляю прайс-лист
    @action(methods=['PUT',], detail=True)
    def upload_price(self, request, *args, **kwargs):
        #
        file_serializer=ShopPriceListSerializer(data=request.data)

        # здесь разрешения должны быть размещены!
        if file_serializer.is_valid():
            shop=Shop.objects.get(id=kwargs['pk'])

            print(request.data.get('price_list'))
            print(request.data)

            file_serializer.update(shop, file_serializer.validated_data)
            return Response(file_serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # почему put, а не post? если старые данные удаляются и только новые остаются, то лучше post!
    @action(methods=['POST', ], detail=True)
    def apply_price(self, request, *args, **kwargs):
        """
        разбираем прайс-лист от магазина
        """
        try:
            shop = Shop.objects.get(id=kwargs['pk'])
        except:
            return Response({'Error': 'Shop does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        #проверка: загружен ли прайс-лист
        if shop.price_list:
            print('Разбираем прайс лист!')

            # Вариант 1
            # для открытия файла по ссылке нам потребуется валидатор URL
            validate_url = URLValidator()
            # получаем адрес вида: http://127.0.0.1:8000/media/Svayznoy/price1.yaml
            price_URL='http://' + request.get_host()+backend.settings.MEDIA_URL+str(shop.price_list)
            print(price_URL)
            # валидируем URL
            try:
                validate_url(price_URL)
            except ValidationError as e:
                return Response({'Error': str(e)}, status=status.HTTP_417_EXPECTATION_FAILED)

            # запрашиваем полезную инфо  - payload - по этому адресу: там наш файл!)
            stream = get(price_URL).content
            #stream = get(price_URL).text
            data = load_yaml(stream, Loader=Loader)
            print(data)

            # Вариант 2
            # with open(stream2) as yaml_file:
            #     data = load_yaml(yaml_file, Loader=Loader)

            # 1. Проверка на магазин и менеджера:
            # name = data['shop'], user_id = request.user.id
            if data['shop'] != shop.name:
                return Response({'Error': 'Invalide shop name in price!'},
                                status=status.HTTP_417_EXPECTATION_FAILED)

            # парсим прайс-лист
            # 1. фиксируем категории товаров (если они есть, конечно):
            # если в словаре нет списка ключа 'categories', то идем дальше:
            if data['categories']:
                # получаем список словарей {id, name} всех категорий ДАННОГО магазина!
                category_list=list(Category.objects.filter(shops__exact=shop.id).values('category_id', 'name'))
                for cat in data['categories']:
                    print(cat)
                    #если такой категории нет в БД - добавляем!
                    if cat not in category_list:
                        # добавляем категорию
                        # Warning! We need to get the Shop object and then add it to shops field.
                        # We can't add an object to ManyToManyField when creating an instance!
                        # делай раз
                        instance = Category.objects.create(category_id=cat['category_id'],name=cat['name'])
                        # делай два
                        instance.shops.add(shop)

            #2. Разносим товары:
            # если в словаре нет списка ключа 'goods', то завершаем работу:
            if data['goods']:
                # идем по списку товаров
                for good in data['goods']:
                    # 2.1 Такой товар уже есть этом в магазине? ищем по имени
                    if not Product.objects.filter(shops__exact=shop.id, name=good['name']).exists():
                        # 2.1.1 создаем новый товар
                        # категория такая вообще есть в этом магазине?
                        try:
                            good_cat=Category.objects.filter(shops__exact=shop).get(category_id=good['category_id'])
                        except Category.DoesNotExist as e:
                            return Response({'Error': 'Category does not exist!'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        except Category.MultipleObjectsReturned as e:
                            return Response({'Error': 'More than one object was found!'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        try:
                            product = Product.objects.create(name=good['name'], category=good_cat)
                            product.shops.add(shop)
                        except:
                            return Response({'Error': 'Product can not be created!'},
                                            status=status.HTTP_400_BAD_REQUEST)

                        try:
                             product_info=ProductInfo.objects.create(model=good['model'],
                                                                article=good['id'],
                                                                quantity=good['quantity'],
                                                                price=good['price'],
                                                                price_rrc=good['price_rrc'],
                                                                product=product,
                                                                shop=shop)
                        except:
                            return Response({'Error': 'ProductInfo can not be created!'},
                                            status=status.HTTP_400_BAD_REQUEST)

                        # 2.1.3 заполняем параметры товара
                        for param_name, param_value in good['parameters'].items():
                            try:
                                param=Parameter.objects.create(name=param_name,
                                                           value=param_value,
                                                           product_info=product_info)
                            except:
                                return Response({'Error': 'Parameter can not be created!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                    else:
                        #если товар уже существует, то меняем цены и увеличиваем количество
                        product = Product.objects.filter(shops__exact=shop.id, name=good['name']).get()
                        #обновляем стоимость и увеличиваем количество товара
                        product_info = ProductInfo.objects.filter(product__exact=product, shop__exact=shop).\
                            update(price=good['price'], price_rrc=good['price_rrc'], quantity=F('quantity')+good['quantity'])



            return Response({'Status': 'Price is applying!'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Price in required'}, status=status.HTTP_428_PRECONDITION_REQUIRED)

    @action(methods=['GET', ], detail=True)
    def get_products(self, request, *args, **kwargs):
        """
        Выдать список товаров магазина
        """
        print('Выдать список товаров магазина!')

        #получаем магазин
        shop = Shop.objects.get(id=kwargs['pk'])
        # если магазин принимает товары
        if shop.state:
            products_list = dict()
            now=datetime.datetime.now()
            products_list['date_time'] = now.strftime("%d-%m-%Y %H:%M")
            products_list['shop_name'] = shop.name
            user=request.user
            products_list['user_name'] = user.email
            products_list['user_type'] = user.type

            #получаем все продукты магазина:
            products=ProductInfo.objects.filter(shop__exact=shop)
            # если есть продукты
            if products:
                for product in products:
                    product_info= {}
                    product_info['product_name']=product.product.name
                    product_info['catogory_name']=product.product.category.name
                    product_info['quantity'] = product.quantity - product.reserved
                    product_info['price'] = product.price_rrc

                    products_list[product.product.name]=product_info

            return Response({'It is all products of shop': products_list}, status=status.HTTP_200_OK)
        else:
            return Response('This shop do not reсieve any orders', status=status.HTTP_200_OK)

