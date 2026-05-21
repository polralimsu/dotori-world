from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('write/', views.write_post, name='write'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
