from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    name = models.CharField(max_length=100)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class FavoriteColor(models.Model):
    user = models.ForeignKey(User, related_name='favorite_colors', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
