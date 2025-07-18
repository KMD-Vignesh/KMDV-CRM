import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from app.models import UserProfile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name  = forms.CharField(max_length=30, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email.strip()).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class UserAddForm(UserCreationForm):
    is_staff     = forms.BooleanField(required=False, label='Staff')
    is_superuser = forms.BooleanField(required=False, label='Superuser')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'is_staff', 'is_superuser')


class UserEditForm(UserChangeForm):
    password = None

    # 1) profile fields first
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=False,
        label='Role'
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    date_of_join = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    designation   = forms.CharField(required=False)
    work_location = forms.CharField(required=False)
    address       = forms.CharField(widget=forms.Textarea, required=False)

    # 2) staff / superuser at the bottom
    is_staff     = forms.BooleanField(required=False, label='Staff')
    is_superuser = forms.BooleanField(required=False, label='Superuser')

    class Meta(UserChangeForm.Meta):
        model  = User
        # explicit order: user → profile → check-boxes
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'role', 'date_of_birth', 'date_of_join',
            'designation', 'work_location', 'address',
            'is_staff', 'is_superuser'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # load profile data
        if self.instance.pk:
            try:
                p = self.instance.userprofile
            except UserProfile.DoesNotExist:
                p = None
            for f in ['role', 'date_of_birth', 'date_of_join',
                      'designation', 'work_location', 'address']:
                self.fields[f].initial = getattr(p, f, None)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = User.objects.filter(email__iexact=email.strip())
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        for f in ['role', 'date_of_birth', 'date_of_join',
                  'designation', 'work_location', 'address']:
            setattr(profile, f, self.cleaned_data[f])
        if commit:
            profile.save()
        return user

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