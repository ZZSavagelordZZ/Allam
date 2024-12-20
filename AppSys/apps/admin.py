from django.contrib import admin
from .models import (
    Patient,
    Appointment,
    Medicine,
    Examination,
    Prescription,
    DoctorBusyHours
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'phone', 'email')
    search_fields = ('first_name', 'last_name', 'phone', 'email')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'time', 'status', 'created_by')
    list_filter = ('status', 'date')
    search_fields = ('patient__first_name', 'patient__last_name')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('examination', 'medicine', 'dosage', 'duration')
    search_fields = ('examination__appointment__patient__first_name', 'medicine__name')

@admin.register(DoctorBusyHours)
class DoctorBusyHoursAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'reason')
    list_filter = ('date',)
    search_fields = ('reason',)

