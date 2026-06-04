from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('charge/', views.do_toss_payment, name='do_toss_payment'),
    path('buy/<int:music_id>/', views.buy_music, name='buy_music'),
    path('payment_success/', views.pay_success, name='pay_success'),
    path('payment_fail/', views.pay_failure, name='pay_failure'),
    path('pay/', views.do_toss_payment, name='toss_pay')
]
