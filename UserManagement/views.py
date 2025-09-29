from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
from django.contrib import messages
from django.http import JsonResponse

from UserManagement import forms, models
from Cryptography.notifications import NotificationManager


# Create your views here.
class Signup(CreateView):
    model = get_user_model()
    form_class = forms.NewUser
    template_name = 'UserManagement/Signup.html'
    success_url = reverse_lazy("hub:Dashboard")

    def form_valid(self, form):
        form.save(commit=True)
        user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is None:
            self.form_invalid(form)
        self.success_url = reverse_lazy(f"hub:{models.UserManager.ROLES_Map[user.role - 1]}Dashboard")
        login(request=self.request, user=user)
        return redirect(to=self.success_url)


class Login(LoginView):
    template_name = 'UserManagement/Login.html'
    authentication_form = forms.UserLogin

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        print(user)
        if user is None:
            messages.error(self.request, "Failure improper pass")
            self.form_invalid(form)
        login(self.request, user)
        self.success_url = reverse_lazy(f"hub:{models.UserGroups.ROLES_Map[user.role - 1]}Dashboard")
        print(self.success_url)
        return redirect(to=self.success_url)


class Logout(LogoutView):
    next_page = reverse_lazy("hub:Home")
    http_method_names = ['get', 'post']  # Allow both GET and POST for logout


class Profile(LoginRequiredMixin, View):
    """User profile page with RSA key generation"""

    def get(self, request):
        context = {
            'user': request.user,
            'has_rsa_keys': request.user.has_rsa_keys(),
            'unread_notifications': NotificationManager.get_recent_notifications(request.user, 10)
        }
        return render(request, 'UserManagement/Profile.html', context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_keys':
            try:
                if request.user.has_rsa_keys():
                    messages.warning(request, 'RSA keys already exist for your account.')
                else:
                    private_pem, public_pem = request.user.generate_rsa_keys()
                    request.user.save()
                    messages.success(request, 'RSA keys generated successfully! You can now access encrypted files.')

                    # Mark key generation notification as read
                    key_notifications = request.user.notifications.filter(
                        notification_type='KEY_GENERATION_REQUIRED',
                        is_read=False
                    )
                    key_notifications.update(is_read=True)

            except Exception as e:
                messages.error(request, f'Failed to generate RSA keys: {str(e)}')

        elif action == 'regenerate_keys':
            try:
                # This will overwrite existing keys
                private_pem, public_pem = request.user.generate_rsa_keys()
                request.user.save()
                messages.success(request, 'RSA keys regenerated successfully! Note: Previously encrypted files may need re-encryption.')
            except Exception as e:
                messages.error(request, f'Failed to regenerate RSA keys: {str(e)}')

        return redirect('UserManagement:Profile')