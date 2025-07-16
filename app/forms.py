import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name  = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


User = get_user_model()
class UserAddForm(UserCreationForm):
    is_staff     = forms.BooleanField(required=False, label='Staff')
    is_superuser = forms.BooleanField(required=False, label='Superuser')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'is_staff', 'is_superuser')

class UserEditForm(UserChangeForm):
    password = None
    is_staff     = forms.BooleanField(required=False, label='Staff')
    is_superuser = forms.BooleanField(required=False, label='Superuser')

    class Meta(UserChangeForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email',
                  'is_staff', 'is_superuser')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }