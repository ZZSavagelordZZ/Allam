# Import necessary modules from Django 
from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin 
# Import custom forms and model from the same Django app (assuming they are in the same directory) 
from .forms import CustomUserCreationForm, CustomUserChangeForm 
from .models import CustomUser 
# Create a custom admin class for our CustomUser model 
class CustomUserAdmin(UserAdmin): 
# Specify the form to be used for adding new users 
    add_form = CustomUserCreationForm 
    # Specify the form to be used for editing existing users 
    form = CustomUserChangeForm 
    # Specify the model that this admin class is associated with 
    model = CustomUser 
    # Register the CustomUser model with the CustomUserAdmin class in the Django admin site 
    #
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('founded_in',)}),
        )
        
    add_fieldsets = (
            (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'first_name', 'last_name', 'password1', 'password2'),
            }),
        )
    #
    list_display = ['email', 'username', 'founded_in', 'is_staff', ] 

admin.site.register(CustomUser, CustomUserAdmin) 

