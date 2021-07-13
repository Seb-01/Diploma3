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
from django.core.mail import EmailMessage
import json

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

    # отправка заказа
    @action(methods=['PUT', ], detail=True)
    def send_order(self, request, *args, **kwargs):
        # получаем экземпляр заказа и его статус:
        order = Order.objects.get(id=kwargs['pk'])
        order_status = order.state
        # Заказчик:
        email_from=self.request.user.email
        # только если это и в ней уже есть позиции:
        if order_status == 'basket':
            serializer = OrderAddItemSerializer(data=request.data)
            print('Отправка заказа!')

            # отправляем email
            # email(ы) администратора(ов) получаем
            admins=User.objects.filter(is_admin=True)
            for admin in admins:
                target_email=admin.email
                # номер заказа
                order_number=str(kwargs['pk'])
                # тема письма
                subject=f'Order # {order_number} Date/Time: {order.dt} Name: {self.request.user.first_name} {self.request.user.last_name}'
                # тело письма
                body_list=[]
                positions=OrderItem.objects.filter(order=order).all()
                # если есть позиции в заказе
                if positions != None:
                    for i,position in enumerate(positions):
                        item_dict={}
                        item_dict['model']=position.product_info.model
                        item_dict['quantity'] = position.quantity
                        body_list.append(item_dict)

                # преобразуем словарь в строку
                body=str(body_list)
                email = EmailMessage(subject,body, email_from, [target_email])
                email.send()
                print(target_email)

            # меняем статус заказа и запрос товаров
            order.state = 'send'
            order.body_order=body_list
            order.save()
            return Response({'The order was successfully sent!':body}, status=status.HTTP_201_CREATED)
        else:
            return Response({'Status':'Wrong order status!'}, status=status.HTTP_400_BAD_REQUEST)

    # Подверждение заказа
    @action(methods=['PUT', ], detail=True)
    def approved_order(self, request, *args, **kwargs):
        # только если это и в ней уже есть позиции:
        # получаем экземпляр заказа и его статус:
        order = Order.objects.get(id=kwargs['pk'])
        order_status = order.state
        if order_status == 'send':
            serializer = OrderAddItemSerializer(data=request.data)
            print('Подтверждение заказа!')
            # отправляем email
            # email(ы) администратора(ов) получаем
            email_from = User.objects.filter(is_admin=True)
            target_email=self.request.user.email

            # все имеющие позиции товара просматриваем
            positions = OrderItem.objects.filter(order=order).all()
            # если есть позиции в наличии
            approved=True
            if positions != None:
                # проверяем конкретную позицию:
                for position in positions:
                    if position.quantity <= ProductInfo.objects.get(id=position.product_info.id).quantity:
                        pass
                    else:
                        approved=False
                        # дальше не идем!
                        break

                # если проверка пройдена
                if approved:
                    # уменьшаем количество товара
                    for position in positions:
                        prod_info=ProductInfo.objects.get(id=position.product_info.id)
                        if prod_info.quantity >= position.quantity:
                            prod_info.quantity=prod_info.quantity-position.quantity
                            prod_info.save()

                    # отправка почты
                    # тема письма
                    order_number = str(kwargs['pk'])
                    subject = f'Approved Order # {order_number} Date/Time: {order.dt} Name: {self.request.user.first_name} {self.request.user.last_name}'
                    body='Order is confirmed!'
                    email = EmailMessage(subject, body, email_from, [target_email])
                    email.send()
                    print(target_email)

                    # меняем статус заказа
                    order.state = 'confirmed'
                    order.save()
                else:
                    return Response({'Status': 'Wrong order positions!'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'The order was successfully approved!': body}, status=status.HTTP_201_CREATED)
        else:
            return Response({'Status': 'Wrong order status!'}, status=status.HTTP_400_BAD_REQUEST)