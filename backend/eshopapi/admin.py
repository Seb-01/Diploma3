from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from users.models import User
from eshopapi.models import Shop
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


# Register your models here.
# Теперь необходимо подключить нашу пользовательскую модель к админке

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""
    # Расширяем исходный класс UserAdmin, предоставляемый администратором Django
    # Позволяет изменить макет страниц добавления и редактирования объекта.
    # fieldsets – это список двух-элементных кортежей, каждый представляет
    # <fieldset> в форме редактирования объекта.
    # Кортеж должен быть в формате (name, options полей), где name это название группы полей,
    # а field_options – словарь с информацией о группе полей, включая список полей для отображения.
    fieldsets = (
        (_('Уникальный идентификатор:'), {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # Список содержащий CSS классы, которые будут добавлены в группу полей
    # Django предоставляет два класса для использования: collapse и wide. Группа полей с классом collapse будет
    # показа в свернутом виде с кнопкой «развернуть». Группа полей с классом wide будет шире по горизонтали.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(Shop)
