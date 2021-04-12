from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

# Create your models here.

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)

class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """

    #: If set to True the manager will be serialized into migrations and will
    #: thus be available in e.g. RunPython operations.
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        #здесь создаем экземпляр класса, которым управляет данный менеджер модели
        #по сути это конструктор User
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    #менеджер модели User
    objects = UserManager()

    # USERNAME_FIELD — строка с именем поля модели, которая используется в качестве уникального идентификатора
    # (unique=True в определении); REQUIRED_FIELDS — список имен полей, которые будут запрашиваться
    # при создании пользователя с помощью команды управления createsuperuser.
    USERNAME_FIELD = 'email'
    # EmailField is a CharField that checks the value for a valid email address using EmailValidator.
    # EmailValidator validates a email through predefined regex which checks ‘@’ and a ‘.’ defined after it.
    # One can change the regex by change options from EmailValidator.
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        # влияет на admin-ку - если default=False в aдминку не зайдешь
        # при этом будет писать всякую чушь: типа проверь email и пароль))
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    is_admin = models.BooleanField(
        _('admin'),
        # администратор магазина
        default=False,
        help_text=_(
            'Flag - whether the user is an administrator.'
        ),
    )

    # возьмется от родительской модели
    """
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    """

    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    # Обязательные поля: убрал - иначе вот такую проблему получаю:
    # При попытке в админке завести суперпользователя получаю ошибку:
    # django.core.exceptions.FieldDoesNotExist: User has no field named 'eshopapi.User.username'
    #REQUIRED_FIELDS = [username, email,]
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.email}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)

