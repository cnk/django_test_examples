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
        read_only_fields = ('url', 'color', 'user')

    def validate(self, data):
        print('In validate. Initial data:')
        print(self.initial_data)
        data['user'] = get_object_or_404(User, username=self.initial_data['username'])
        data['color_ids'] = self.initial_data.getlist('choice')
        return data
        
    def create(self, validated_data):
        new_records = []
        for id in validated_data['color_ids']:
            rec = FavoriteColor(user=validated_data['user'], color_id=id)
            rec.full_clean()
            rec.save()
            new_records.append(rec)
        return new_records
            
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

    @list_route(methods=['post', 'put'])
    def record_favorites(self, request):
        print('in record_favorites')
        serializer = FavoriteColorSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
