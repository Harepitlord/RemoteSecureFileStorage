from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from UserManagement import models


class NewUser(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=models.UserGroups.ROLES[1:])

    class Meta:
        model = get_user_model()
        fields = ('name', 'country', 'phone_no', 'email', 'password',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()


class UserLogin(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=models.UserGroups.ROLES)

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'country', 'phone_no', 'role', 'port')


class CustomUserChangeForm(UserChangeForm):
    role = forms.ChoiceField(choices=models.UserGroups.ROLES)

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'country', 'phone_no', 'port')
