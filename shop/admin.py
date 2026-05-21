from django.contrib import admin
from .models import Music, UserMusic

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'price')
    search_fields = ('title', 'artist')

@admin.register(UserMusic)
class UserMusicAdmin(admin.ModelAdmin):
    list_display = ('user', 'music', 'purchased_at')
    list_filter = ('purchased_at',)
