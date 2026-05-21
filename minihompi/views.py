from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from accounts.models import User
from django.contrib.auth.decorators import login_required
import random
import boto3
import os
from .models import IlchonPyeong
from .forms import IlchonPyeongForm
from django.contrib import messages
from django.utils.translation import gettext as _

def index(request, username):
    hompi_user = get_object_or_404(User, username=username)
    posts = hompi_user.posts.all().prefetch_related('comments', 'comments__author')
    ilchonpyeongs = hompi_user.ilchonpyeongs.all().select_related('author')
    
    friendship_status = None
    can_write_ilchon = False
    if request.user.is_authenticated:
        if request.user == hompi_user:
            can_write_ilchon = True
        else:
            rel1 = request.user.friend_requests_sent.filter(to_user=hompi_user).first()
            rel2 = request.user.friend_requests_received.filter(from_user=hompi_user).first()
            
            if rel1:
                friendship_status = rel1.status
                if rel1.status == 'ACCEPTED': can_write_ilchon = True
            elif rel2:
                friendship_status = rel2.status
                if rel2.status == 'ACCEPTED': can_write_ilchon = True
                               
    return render(request, 'minihompi/index.html', {
        'hompi_user': hompi_user, 
        'posts': posts,
        'ilchonpyeongs': ilchonpyeongs,
        'can_write_ilchon': can_write_ilchon,
        'friendship_status': friendship_status
    })

@login_required
def add_ilchonpyeong(request, username):
    hompi_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = IlchonPyeongForm(request.POST)
        if form.is_valid():
            ilchon = form.save(commit=False)
            ilchon.hompi_user = hompi_user
            ilchon.author = request.user
            ilchon.save()
            messages.success(request, _('Ilchon-pyeong saved.'))
    return redirect('minihompi:index', username=username)

@login_required
def delete_ilchonpyeong(request, ilchon_id):
    ilchon = get_object_or_404(IlchonPyeong, id=ilchon_id)
    hompi_user = ilchon.hompi_user
    if request.user == ilchon.author or request.user == hompi_user:
        ilchon.delete()
        messages.success(request, _('Ilchon-pyeong deleted.'))
    return redirect('minihompi:index', username=hompi_user.username)

@login_required
def pado_taki(request):
    friends_relations = request.user.friend_requests_sent.filter(status='ACCEPTED')
    friends = [rel.to_user for rel in friends_relations]
    friends_relations_recv = request.user.friend_requests_received.filter(status='ACCEPTED')
    friends.extend([rel.from_user for rel in friends_relations_recv])
    
    if friends:
        random_friend = random.choice(friends)
        return redirect('minihompi:index', username=random_friend.username)
    else:
        return redirect('minihompi:index', username=request.user.username)

def translate_text(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        target_lang = request.POST.get('target_lang', 'en') # 'en', 'ko', 'ja'
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        
        try:
            client = boto3.client('translate', region_name=os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-2'))
            result = client.translate_text(
                Text=text,
                SourceLanguageCode='auto',
                TargetLanguageCode=target_lang
            )
            return JsonResponse({'translated_text': result.get('TranslatedText')})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
