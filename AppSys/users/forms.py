from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from .models import CustomUser 
class CustomUserCreationForm(UserCreationForm): 
    class Meta(UserCreationForm.Meta): 
        model = CustomUser 
        fields = ('username', 'email', 'role') 
class CustomUserChangeForm(UserChangeForm): 
    class Meta: 
        model = CustomUser 
        fields = ('username', 'email', 'role') 
class CustomLoginForm(AuthenticationForm): 
    class Meta: 
        model = CustomUser 
class CustomPasswordResetForm(PasswordResetForm): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['email'].widget.attrs.update({'class': 'form-control'}) 
