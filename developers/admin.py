from django.contrib import admin
from .models import Developer, Game, GameImage


admin.site.register(Developer)


class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 3  

class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'developer', 'status', 'price', 'release_date']
    list_filter = ['status', 'game_type', 'developer']
    search_fields = ['title']

admin.site.register(Game, GameAdmin)
