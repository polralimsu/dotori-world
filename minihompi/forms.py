from django import forms
from .models import IlchonPyeong

class IlchonPyeongForm(forms.ModelForm):
    class Meta:
        model = IlchonPyeong
        fields = ('text',)
