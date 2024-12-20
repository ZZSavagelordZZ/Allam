from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('patient_detail', args=[str(self.id)])

class App(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('patient_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'App'
        verbose_name_plural = 'Apps'

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_appointments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Check if the time slot is available
        end_time = (datetime.combine(self.date, self.time) + timedelta(minutes=30)).time()
        overlapping = Appointment.objects.filter(
            date=self.date,
            time__lt=end_time,
            time__gt=self.time
        ).exclude(id=self.id)
        
        if overlapping.exists():
            raise ValidationError('This time slot overlaps with another appointment')
        
        # Check if the time slot is in doctor's busy hours
        busy_hours = DoctorBusyHours.objects.filter(
            date=self.date,
            start_time__lte=self.time,
            end_time__gte=self.time
        )
        if busy_hours.exists():
            raise ValidationError('This time slot is marked as busy by the doctor')

    def __str__(self):
        return f"{self.patient} - {self.date} {self.time}"

    def get_absolute_url(self):
        return reverse('appointment_detail', args=[str(self.id)])

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    dosage_instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('medicine_detail', args=[str(self.id)])

class Examination(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Examination for {self.appointment}"

    def get_absolute_url(self):
        return reverse('examination_detail', args=[str(self.id)])

class Prescription(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine} for {self.examination.appointment.patient}"

class DoctorBusyHours(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time')

        # Check if there are any appointments in this time slot
        appointments = Appointment.objects.filter(
            date=self.date,
            time__gte=self.start_time,
            time__lt=self.end_time
        )
        if appointments.exists():
            raise ValidationError('There are appointments scheduled during this time')

    def __str__(self):
        return f"Busy: {self.date} {self.start_time}-{self.end_time}"

