"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from users.views import UserViewSet
from rest_framework.authtoken import views
from users.views import AuthViewSet
from shops_n_goods.views import ShopsViewSet
from orders.views import OrdersViewSet

# для управления настройками Django
from django.conf import settings

from django.conf.urls.static import static
"""
Return a URL pattern for serving files in debug mode.

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'api/v1/users', UserViewSet)

# Note that if the viewset does not include a queryset attribute then you must
# set basename when registering the viewset.
# The basename argument is used to specify the initial part of the view name pattern
# у нас будет: api/auth/login, api/auth/logout и т.д.
router.register(r'api/v1/auth', AuthViewSet)
#router.register(r'api/v1/shops', ShopsViewSet, basename='shops')
router.register(r'api/v1/shops', ShopsViewSet)
router.register(r'api/v1/orders', OrdersViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns += [
    path('', include(router.urls)),
    # Default login/logout views
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token) # вьюха для получения токена
]
# если настройки в режиме DEBUG, то MEDIA_URL также нужно добавить.
# В противном случае не получится увидеть загружаемые файлы.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

