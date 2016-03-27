from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from .models import Color, FavoriteColor


def index(request):
    if request.POST:
        data = request.POST
        choices = request.POST.getlist('choice')
    else:
        data = None
        choices = None
    context = {'colors': Color.objects.all(), 'data': data, 'choices': choices}
    return render(request, 'example/index.html', context)

################## API ########################

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

                                        
# Serializers define the API representation.
class ColorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Color
        fields = ('url', 'name')

# ViewSets define the view behavior.
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

                                        
# Serializers define the API representation.
class FavoriteColorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FavoriteColor
        fields = ('url', 'color', 'user')

# ViewSets define the view behavior.
class FavoriteColorViewSet(viewsets.ModelViewSet):
    queryset = FavoriteColor.objects.all()
    serializer_class = FavoriteColorSerializer

                                        
    
