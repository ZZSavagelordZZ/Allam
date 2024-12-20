from django.contrib.auth.models import AbstractUser 
from django.db import models 
# Here, we are creating a new class called CustomUser that extends Django's built-in AbstractUser class. 
class CustomUser(AbstractUser): 
    # User role choices
    DOCTOR = 'doctor'
    SECRETARY = 'secretary'
    ROLE_CHOICES = [
        (DOCTOR, 'Doctor'),
        (SECRETARY, 'Secretary'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=DOCTOR,
    )
    email = models.EmailField(unique=True)  # Make email required and unique
    founded_in = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
    

