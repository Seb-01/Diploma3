from rest_framework import viewsets
from eshopapi.models import User
from eshopapi.serializers import UserSerializer

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer