import http.client
import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Music, UserMusic, UserOrder
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponse

@login_required
def index(request):
    musics = Music.objects.all()
    from django.db.models import Exists, OuterRef
    purchased = UserMusic.objects.filter(user=request.user, music=OuterRef('pk'))
    musics = musics.annotate(is_purchased=Exists(purchased))
    return render(request, 'shop/index.html', {'musics': musics})


@login_required
def buy_music(request, music_id):
    music = get_object_or_404(Music, id=music_id)
    if request.user.dotori_balance >= music.price:
        if not UserMusic.objects.filter(user=request.user, music=music).exists():
            request.user.dotori_balance -= music.price
            request.user.save()
            UserMusic.objects.create(user=request.user, music=music)
            messages.success(request, _('Successfully purchased music: {}').format(music.title))
        else:
            messages.warning(request, _('You already own this music.'))
    else:
        messages.error(request, _('Not enough Dotori.'))
    return redirect('shop:index')

@login_required
def do_toss_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', '10')
        money = int(amount) * 100;
        order = UserOrder.objects.create(user=request.user, amount=amount, price=money);
        order.save()
        return render(request, 'shop/pay.html', {
            'amount': amount,
            'uuid': order.uuid
        })
    return render(request, 'shop/charge.html')

@login_required
def pay_success(request):
    if request.method == 'GET':
        amount = request.GET.get('amount')
        order_id = request.GET.get('orderId')
        payment_key = request.GET.get('paymentKey')
        order = UserOrder.objects.filter(uuid=order_id).get()

        if order.price == int(amount):
            conn = http.client.HTTPSConnection("api.tosspayments.com")
            payload = "{\"paymentKey\":\"" + payment_key + "\",\"orderId\":\"" + order_id + "\",\"amount\":" + amount + "}"

            headers = {
                'Authorization': "Basic " + urlsafe_base64_encode(force_bytes(os.environ.get('TOSS_SECRET_KEY') + ':')),
                'Content-Type': "application/json"
            }

            conn.request("POST", "/v1/payments/confirm", payload, headers)

            res = conn.getresponse()
            data = res.read()

            decoded = data.decode("utf-8")
            result = json.loads(decoded)
            if result['status'] == 'DONE':
                request.user.dotori_balance += order.amount
                request.user.save()
                messages.success(request, _('Successfully charged {} Dotori.').format(order.amount))
            else:
                messages.error(request, _('Failed confirming payment.'))
        else:
            messages.error(request, _('Failed payment.'))
        
        order.delete()
    return redirect('shop:index')

@login_required
def pay_failure(request):
    if request.method == 'GET':
        order_id = request.GET.get('orderId')
        order = UserOrder.objects.filter(uuid=order_id).get()
        order.delete();
    
    messages.error(request, _('Failed payment.'))
    return redirect('shop:index')
