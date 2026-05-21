from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('charge/', views.do_toss_payment, name='do_toss_payment'),
    path('request_pay/', views.get_pay_id, name='get_pay_id'),
    path('buy/<int:music_id>/', views.buy_music, name='buy_music'),
    path('payment_success/', views.pay_success, name='pay_success'),
    path('payment_fail/', views.pay_failure, name='pay_failure'),
]
