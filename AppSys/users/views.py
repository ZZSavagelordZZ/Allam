from django.shortcuts import render,redirect

# Create your views here.
# Import necessary modules and classes from Django 
from django.urls import reverse_lazy 
from django.views.generic import CreateView 
from .forms import CustomUserCreationForm, CustomLoginForm 
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView

# Define a class called SignUpView that inherits from Django's CreateView class 
class SignUpView(CreateView): 
    # Specify the form class to be used for user registration 
    form_class = CustomUserCreationForm 
    # Set the URL to redirect to upon successful user registration (uses reverse_lazy for deferred URL resolution) 
    success_url = reverse_lazy('login') 
    # Specify the template (HTML file) to be used for rendering the signup page 
    template_name = 'signup.html' 

    # Define a function called logoutUser that logs out the current user and redirects them to the 'home' URL 
def logoutUser(request): 
     # Use Django's logout function to log out the current user 
    logout(request) 
    # Redirect the user to the 'home' URL after logging out 
    return redirect('home') 

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        # Redirect based on user role
        if self.request.user.role == 'doctor':
            return reverse_lazy('doctor_dashboard')
        else:
            return reverse_lazy('secretary_dashboard')

