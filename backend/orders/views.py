from django.shortcuts import render
from rest_framework import viewsets
from eshopapi.models import Order, Contact, OrderItem, ProductInfo
from users.models import User
from orders.serializers import OrderSerializer, OrderCreateSerializer, OrderAddItemSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from eshopapi.models import STATE_CHOICES
from datetime import datetime
from rest_framework.parsers import JSONParser

# Create your views here.
class OrdersViewSet(viewsets.ModelViewSet):
    """
    Допущены admin и овнеры своих заказов
    """
    # пока два варианта оставим
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    # The set of valid parsers for a view is always defined as a list of classes.
    # When request.data is accessed, REST framework will examine the Content-Type header on the incoming request,
    # and determine which parser to use to parse the request content.
    parser_classes = [JSONParser]

    # создание заказа явную команду
    @action(methods=['POST',], detail=True)
    def create_order(self, request, *args, **kwargs):
        """

        """
        serializer = OrderCreateSerializer(data=request.data)
        serializer.save(user=self.request.user)
        return Response({'Order': 'Order was created!'}, status=status.HTTP_201_CREATED)

    # создание заказа переопределяем
    def create(self, request, *args, **kwargs):
        """
        Переопределяем миксин для того, чтобы дозаполнить данные
        """
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            # нужно добавить статус заявки и контакты подтянуть
            # через get(), чтобы получить конкретный экземпляр объекта
            user=User.objects.filter(email=request.user.email).get()
            print(user)
            # потребуется экземпляр (!) контакта, а не QuerySet
            contact=Contact.objects.filter(user=user.pk).get()
            serializer.save(user=request.user, dt=datetime.now(), state='new', contact=contact)
            print(serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # добавление в заказ позиции
    @action(methods=['POST',], detail=True)
    def add_item(self, request, *args, **kwargs):
        """
        Добавление позиций в заказ
        """
        print(request)
        # получаем экземпляр заказа и его статус:
        order = Order.objects.get(id=kwargs['pk'])
        order_status=order.state
        # только если это новый заказ или в нем уже есть позиции:
        if order_status == 'new' or order_status == 'basket':
            # здесь свой сериализатор
            serializer = OrderAddItemSerializer(data=request.data)
            print(serializer)
            print(serializer.initial_data)
            if serializer.is_valid():
                # создаем новый инстанс позиции в заказе
                product_info=ProductInfo.objects.get(id=serializer.initial_data['id_product_info'])
                try:
                    item=OrderItem.objects.create(order=order, product_info=product_info,
                                                  quantity=serializer.initial_data['quantity'])
                except:
                    return Response({'Error': 'Something is wrong with the order position!'}, status=status.HTTP_400_BAD_REQUEST)
                if order_status == 'new':
                    order.state = 'basket'
                    order.save()
                print(item)
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'Status':'Wrong order status!'}, status=status.HTTP_400_BAD_REQUEST)