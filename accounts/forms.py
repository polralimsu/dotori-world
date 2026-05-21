from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from shop.models import UserMusic

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'nickname', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('nickname', 'profile_image', 'main_video', 'profile_text', 'bgm')
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            purchased_music_ids = UserMusic.objects.filter(user=user).values_list('music_id', flat=True)
            self.fields['bgm'].queryset = self.fields['bgm'].queryset.filter(id__in=purchased_music_ids)
            self.fields['bgm'].empty_label = "No BGM"
