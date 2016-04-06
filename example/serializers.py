from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Color, FavoriteColor
from pprint import pprint  # noqa


class ColorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Color
        fields = ('url', 'name')


class FavoriteColorSerializer(serializers.HyperlinkedModelSerializer):
    color_name = serializers.CharField(read_only=True, source='color.name')

    class Meta:
        model = FavoriteColor
        fields = ('url', 'color', 'color_name', 'user')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    favorite_colors = FavoriteColorSerializer(many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'favorite_colors')
        read_only_fields = ('username', 'is_staff')

    def get_favorite_colors(self, instance):
        return FavoriteColor.objects.filter(user=instance).values_list('color__name', flat=True)

    def validate(self, data):
        data['color_ids'] = self.initial_data.getlist('choice', None)
        return data

    def update(self, instance, validated_data):
        print('initial data is')
        print(self.initial_data)
        print('validated_data is')
        print(validated_data)
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
