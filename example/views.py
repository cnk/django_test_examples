from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.http.request import QueryDict
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, api_view
from rest_framework.response import Response
from .models import Color, FavoriteColor
from .serializers import UserSerializer, ColorSerializer, FavoriteColorSerializer
from pprint import pprint  # noqa


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
        assert isinstance(request.data, QueryDict), 'request.data was not a QueryDict'
        user = get_object_or_404(User, username=request.data['username'])
        color_ids = request.data.getlist('choices')
        for color_id in color_ids:
            record = FavoriteColor(user=user, color_id=color_id)
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


# This is a stand-alone version of the record_favorite_colors view in UserSerializer
@api_view(['POST', 'PUT'])
def update_favorite_colors(request):
    user = get_object_or_404(User, username=request.data['username'])
    serializer = UserSerializer(user, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
