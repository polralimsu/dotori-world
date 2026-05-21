from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Friendship

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('nickname', 'profile_image', 'main_video', 'profile_text', 'dotori_balance', 'bgm')}),
    )
    list_display = ('username', 'email', 'nickname', 'dotori_balance', 'is_staff')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
