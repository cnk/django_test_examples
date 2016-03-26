from django.contrib import admin
from example.models import Color, FavoriteColor

class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


class FavoriteColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'color', )

    
# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(FavoriteColor, FavoriteColorAdmin)
