from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Find username (by email)
    path('find-username/', views.find_username, name='find_username'),

    # Password reset (Django built-in views with custom templates)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='email/password_reset_email.html',
             subject_template_name='email/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/',
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset-complete/',
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # Existing routes
    path('friends/', views.friends_list, name='friends'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('search/', views.search_users, name='search_users'),
    path('friend/send/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
]
