from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileEditForm
from .models import Friendship, User
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q


from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from .utils import account_activation_token


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        # Save user but keep inactive until email verification
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Send activation email
        protocol = 'https' if self.request.is_secure() else 'http'
        subject = _('DOTORi World - Verify your email')
        message = render_to_string('email/activation_email.html', {
            'user': user,
            'protocol': protocol,
            'domain': self.request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(self.request, _('Please check your email to activate your account.'))
        return redirect(self.success_url)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, _('Your account has been activated.'))
        return redirect('accounts:login')
    else:
        messages.error(request, _('Activation link is invalid!'))
        return redirect('accounts:signup')


def find_username(request):
    """Find username by email address."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            messages.success(request, _('Your username is: %(username)s') % {'username': user.username})
        except User.DoesNotExist:
            messages.error(request, _('No account found with that email address.'))
    return render(request, 'accounts/find_username.html')


@login_required
def friends_list(request):
    friends_relations = request.user.friend_requests_sent.filter(status='ACCEPTED')
    friends = [rel.to_user for rel in friends_relations]
    friends_relations_recv = request.user.friend_requests_received.filter(status='ACCEPTED')
    friends.extend([rel.from_user for rel in friends_relations_recv])

    pending_requests = request.user.friend_requests_received.filter(status='PENDING')

    return render(request, 'accounts/friends.html', {'friends': friends, 'pending_requests': pending_requests})


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(Q(username__icontains=query) | Q(nickname__icontains=query)).exclude(id=request.user.id)
    return render(request, 'accounts/search.html', {'users': users, 'query': query})


@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if request.user != to_user:
        Friendship.objects.get_or_create(from_user=request.user, to_user=to_user, defaults={'status': 'PENDING'})
        messages.success(request, _('Friend request sent.'))
    return redirect('minihompi:index', username=username)


@login_required
def accept_friend_request(request, request_id):
    friend_req = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='PENDING')
    friend_req.status = 'ACCEPTED'
    friend_req.save()
    messages.success(request, _('Friend request accepted.'))
    return redirect('accounts:friends')


@login_required
def reject_friend_request(request, request_id):
    friend_req = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='PENDING')
    friend_req.delete()
    messages.success(request, _('Friend request rejected.'))
    return redirect('accounts:friends')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            bgm_changed = 'bgm' in form.changed_data
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            if bgm_changed:
                from django.urls import reverse
                from django.http import HttpResponse
                redirect_url = reverse('minihompi:index', kwargs={'username': request.user.username})
                return HttpResponse(f'<script>window.parent.location.href = "{redirect_url}";</script>')
            return redirect('minihompi:index', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user, user=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})
