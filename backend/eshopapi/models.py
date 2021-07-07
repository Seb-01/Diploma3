from django.db import models
from users.models import User

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

MEASURE_TYPE_CHOICES = (
    ('int', 'Целое значение'),
    ('uint', 'Неотрицательное целое значение'),
    ('float', 'С плаваующей точкой значение'),
    ('ufloat', 'Неотрицательное с плаваующей точкой значение'),
    ('string', 'Строковое значение'),
)


class Shop(models.Model):
    """
    У магазина есть url или имя файла, из которого будут загружаться товары
    """
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    # Принимает заказы или нет?
    state = models.BooleanField(verbose_name='Статус получения заказов', default=True)

    # upload_to также может быть вызываемым параметром, который возвращает строку.
    # Этот вызываемый параметр принимает два параметра, экземпляр (instance) и имя файла (filename)
    def user_directory_path(self, filename):
        # file will be uploaded to MEDIA_ROOT/<name>/<filename>
        return '{0}/{1}'.format(self.name, filename)

    # файл с прайс-листом
    # FileField используется для хранения файлов в базе данных
    price_list = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        # по убыванию
        ordering = ('-name',)

    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Категории связаны с магазинами через m2m. Вложенных категорий не предусмотрено
    """
    # мне нужно самому задавать и контролировать id при добавлении записей
    category_id = models.PositiveIntegerField(verbose_name='id категории')
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)
        # constraints = [
        #     models.UniqueConstraint(fields=['category_id', 'shops'], name='unique_category'),
        # ]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='products_in_shop', blank=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    article = models.PositiveIntegerField(verbose_name='Артикул')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='shops', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    reserved = models.PositiveIntegerField(verbose_name='Зарезервировано', default=0)
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'article'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'Model: {self.model}/ Article: {self.article}'


class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name='Параметр')
    value = models.CharField(verbose_name='Значение', max_length=100)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        ordering = ('-name',)
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'name'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return self.name

class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.user} {self.city} {self.street} {self.house}'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name='Контакт',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"
        ordering = ('-dt',)

    def __str__(self):
        return f'Заказ № {self.id} {self.user} {str(self.dt)}'

    # @property
    # def sum(self):
    #     return self.ordered_items.aggregate(total=Sum("quantity"))["total"]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)

    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]

    def __str__(self):
        return f'Position in order № {self.id} {self.product_info} Quantity={self.quantity}'