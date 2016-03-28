from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
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
    favorite_colors = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'favorite_colors')

    def get_favorite_colors(self, instance):
        return FavoriteColor.objects.filter(user=instance).values_list('color__name', flat=True)
        
    def validate(self, data):
        data['color_ids'] = self.initial_data.getlist('choice', None)
        return data
        
    def update(self, instance, validated_data):
        current_favs = FavoriteColor.objects.filter(user=instance).values_list('color_id', flat=True)
        # deletes
        if current_favs:
            for id in current_favs:
                if id not in validated_data['color_ids']:
                    FavoriteColor.objects.filter(user=instance, color_id=id).delete()
        # adds
        for id in validated_data['color_ids']:
            if id not in current_favs:
                rec = FavoriteColor(user=instance, color_id=id)
                rec.full_clean()
                rec.save()
        return instance


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['post', 'put'])
    def record_favorite_colors(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        serializer = UserSerializer(user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
                                        
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

    @list_route(methods=['post', 'put'])
    def add_multiple(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        colors = request.data.getlist('choice')
        for color in colors:
            record = FavoriteColor(user=user, color_id=color)
            record.full_clean()
            record.save()
        return Response(status=status.HTTP_201_CREATED)
