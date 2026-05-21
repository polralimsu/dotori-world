from django.urls import path
from . import views

app_name = 'minihompi'

urlpatterns = [
    path('api/translate/', views.translate_text, name='translate'),
    path('pado-taki/', views.pado_taki, name='pado_taki'),
    path('<str:username>/', views.index, name='index'),
    path('<str:username>/ilchonpyeong/', views.add_ilchonpyeong, name='add_ilchonpyeong'),
    path('ilchonpyeong/<int:ilchon_id>/delete/', views.delete_ilchonpyeong, name='delete_ilchonpyeong'),
]
