from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, api_view
from rest_framework.response import Response
from .models import Color, FavoriteColor
from .serializers import UserSerializer, ColorSerializer, FavoriteColorSerializer
from pprint import pprint


def index(request):
    if request.POST:
        data = request.POST
        choices = request.POST.getlist('choice')
    else:
        data = None
        choices = None
    context = {'colors': Color.objects.all(), 'data': data, 'choices': choices}
    return render(request, 'example/index.html', context)

# ################# API ########################


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class FavoriteColorViewSet(viewsets.ModelViewSet):
    queryset = FavoriteColor.objects.all()
    serializer_class = FavoriteColorSerializer

    @list_route(methods=['post', 'put'])
    def add_multiple(self, request):
        print('in add_multiple, request.data is:')
        print(request.data)
        print('and the cookies are:')
        print(request.COOKIES)
        user = get_object_or_404(User, username=request.data['username'])
        colors = request.data.getlist('choice')
        for color in colors:
            record = FavoriteColor(user=user, color_id=color)
            record.full_clean()
            record.save()
        return Response(status=status.HTTP_201_CREATED)


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


@api_view(['POST', 'PUT'])
def update_favorite_colors(request):
    print('in update_favorite_colors data comes in as:')
    pprint(request.data)
    user = get_object_or_404(User, username=request.data['username'])
    serializer = UserSerializer(user, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
