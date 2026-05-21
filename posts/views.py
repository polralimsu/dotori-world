from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .models import Post
from django.contrib import messages
from django.utils.translation import gettext as _

@login_required
def write_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, _('Post uploaded successfully.'))
            return redirect('minihompi:index', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/write.html', {'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('minihompi:index', username=post.author.username)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        messages.success(request, _('Post deleted.'))
    return redirect('minihompi:index', username=post.author.username)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_author = comment.post.author
    if request.user == comment.author or request.user == post_author:
        comment.delete()
        messages.success(request, _('Comment deleted.'))
    return redirect('minihompi:index', username=post_author.username)
