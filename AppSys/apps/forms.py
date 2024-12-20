from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment, DoctorBusyHours, Examination, Prescription
from django import forms
from .models import Medicine
from .models import Patient
from datetime import datetime

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),
            }
        )
    )
    
    time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '1800'
            }
        )
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'time']
        widgets = {
            'patient': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%;'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all().order_by('first_name', 'last_name')
        self.fields['patient'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            # Combine date and time for easier comparison
            appointment_datetime = datetime.combine(date, time)
            
            # Check for busy hours
            busy_hours = DoctorBusyHours.objects.filter(date=date)
            
            for busy_hour in busy_hours:
                busy_start = datetime.combine(busy_hour.date, busy_hour.start_time)
                busy_end = datetime.combine(busy_hour.date, busy_hour.end_time)
                
                if busy_start <= appointment_datetime <= busy_end:
                    raise forms.ValidationError(
                        f"Doctor is not available at this time due to: {busy_hour.reason}. "
                        f"Busy hours are from {busy_hour.start_time.strftime('%I:%M %p')} "
                        f"to {busy_hour.end_time.strftime('%I:%M %p')}."
                    )

        return cleaned_data

class DoctorBusyHoursForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),
            }
        )
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '1800'
            }
        )
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '1800'
            }
        )
    )

    class Meta:
        model = DoctorBusyHours
        fields = ['date', 'start_time', 'end_time', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Enter the reason for busy hours'
            })
        }

class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ['symptoms', 'diagnosis', 'notes']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Enter patient symptoms'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Enter diagnosis'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Enter any additional notes'
            })
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine', 'dosage', 'duration', 'notes']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control select2'}),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1 tablet twice daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '2',
                'placeholder': 'Additional instructions'
            })
        }

PrescriptionFormSet = forms.inlineformset_factory(
    Examination,
    Prescription,
    form=PrescriptionForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class SecretaryForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'dosage_instructions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            }),
            'dosage_instructions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
            }),
        }        

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': "Please enter a correct email and password.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)        