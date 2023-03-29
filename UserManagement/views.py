from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from UserManagement import forms, models


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