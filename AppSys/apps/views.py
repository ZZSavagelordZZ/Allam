from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from django.utils.timezone import timedelta
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone
from .models import Appointment
from .forms import MedicineForm


from .models import (
    Patient, Appointment, Medicine, 
    Examination, Prescription, DoctorBusyHours
)
from .forms import AppointmentForm, DoctorBusyHoursForm, ExaminationForm, PrescriptionFormSet, SecretaryForm

class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['secretary', 'doctor']

class IsSecretaryMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'secretary'

class IsDoctorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'doctor'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Total Patients
        context['total_patients'] = Patient.objects.count()

        # Today's Appointments
        context['todays_appointments'] = Appointment.objects.filter(
            date=today
        ).count()

        # Pending Appointments
        context['pending_appointments'] = Appointment.objects.filter(
            status='pending'
        ).count()

        # Completed Appointments This Week
        context['completed_this_week'] = Appointment.objects.filter(
            date__range=[week_start, week_end],
            status='completed'
        ).count()

        # Get upcoming appointments for the calendar
        context['upcoming_appointments'] = Appointment.objects.filter(
            date__gte=today
        ).order_by('date', 'time')

        return context

@login_required
@require_GET
def calendar_events(request):
    # Parse the start and end dates from the request
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')
    
    try:
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d').date()
    except ValueError:
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)

    # Get appointments
    appointments = Appointment.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('patient')
    
    # Get busy hours
    busy_hours = DoctorBusyHours.objects.filter(
        date__range=[start_date, end_date]
    )
    
    events = []
    
    # Add appointments to events
    for appointment in appointments:
        start_datetime = datetime.combine(appointment.date, appointment.time)
        end_datetime = start_datetime + timezone.timedelta(minutes=30)
        
        events.append({
            'id': f'appointment_{appointment.id}',
            'title': f'{appointment.patient.first_name} {appointment.patient.last_name}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'url': reverse('appointment_detail', args=[appointment.id]),
            'className': f'appointment-event status-{appointment.status}',
            'description': f'Status: {appointment.status}'
        })
    
    # Add busy hours to events
    for busy in busy_hours:
        start_datetime = datetime.combine(busy.date, busy.start_time)
        end_datetime = datetime.combine(busy.date, busy.end_time)
        
        events.append({
            'id': f'busy_{busy.id}',
            'title': 'Busy - ' + busy.reason,
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'className': 'busy-hours-event',
            'description': busy.reason
        })
    
    return JsonResponse(events, safe=False)

# Basic Patient Views
class PatientListView(LoginRequiredMixin, IsStaffMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'

class PatientDetailView(LoginRequiredMixin, IsStaffMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'

class PatientCreateView(LoginRequiredMixin, IsSecretaryMixin, CreateView):
    model = Patient
    template_name = 'patients/patient_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email', 'address']
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Patient {form.instance.first_name} {form.instance.last_name} created successfully!')
        return response

class PatientUpdateView(LoginRequiredMixin, IsStaffMixin, UpdateView):
    model = Patient
    template_name = 'patients/patient_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email', 'address']

class PatientDeleteView(LoginRequiredMixin, IsStaffMixin, DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')

# Basic Appointment Views
class AppointmentListView(LoginRequiredMixin, IsStaffMixin, ListView):
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'

class AppointmentDetailView(LoginRequiredMixin, IsStaffMixin, DetailView):
    model = Appointment
    template_name = 'appointments/appointment_detail.html'

class AppointmentCreateView(LoginRequiredMixin, IsStaffMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Appointment created successfully!')
        return response

class AppointmentUpdateView(LoginRequiredMixin, IsStaffMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment_list')

class AppointmentDeleteView(LoginRequiredMixin, IsStaffMixin, DeleteView):
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointment_list')

# Doctor Busy Hours Views
class DoctorBusyHoursListView(LoginRequiredMixin, IsDoctorMixin, ListView):
    model = DoctorBusyHours
    template_name = 'busy_hours/busyhours_list.html'
    context_object_name = 'busy_hours'
    ordering = ['-date', '-start_time']

class DoctorBusyHoursCreateView(LoginRequiredMixin, IsDoctorMixin, CreateView):
    model = DoctorBusyHours
    form_class = DoctorBusyHoursForm
    template_name = 'busy_hours/busyhours_form.html'
    success_url = reverse_lazy('busy_hours')

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        return super().form_valid(form)

class DoctorBusyHoursUpdateView(LoginRequiredMixin, IsDoctorMixin, UpdateView):
    model = DoctorBusyHours
    form_class = DoctorBusyHoursForm
    template_name = 'busy_hours/busyhours_form.html'
    success_url = reverse_lazy('busy_hours')

class DoctorBusyHoursDeleteView(LoginRequiredMixin, IsDoctorMixin, DeleteView):
    model = DoctorBusyHours
    template_name = 'busy_hours/busyhours_confirm_delete.html'
    success_url = reverse_lazy('busy_hours')

# Medicine Views
class MedicineListView(LoginRequiredMixin, IsDoctorMixin, ListView):
    model = Medicine
    template_name = 'medicines/medicine_list.html'
    context_object_name = 'medicines'

class MedicineDetailView(LoginRequiredMixin, IsDoctorMixin, DetailView):
    model = Medicine
    template_name = 'medicines/medicine_detail.html'

class MedicineCreateView(LoginRequiredMixin, IsDoctorMixin, CreateView):
    model = Medicine
    template_name = 'medicines/medicine_form.html'
    fields = ['name', 'description', 'dosage_instructions']
    success_url = reverse_lazy('medicine_list')

class MedicineUpdateView(LoginRequiredMixin, IsDoctorMixin, UpdateView):
    model = Medicine
    template_name = 'medicines/medicine_form.html'
    fields = ['name', 'description', 'dosage_instructions']
    success_url = reverse_lazy('medicine_list')

class MedicineDeleteView(LoginRequiredMixin, IsDoctorMixin, DeleteView):
    model = Medicine
    template_name = 'medicines/medicine_confirm_delete.html'
    success_url = reverse_lazy('medicine_list')

# Examination Views
class ExaminationCreateView(LoginRequiredMixin, IsDoctorMixin, CreateView):
    model = Examination
    form_class = ExaminationForm
    template_name = 'examinations/examination_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['prescription_formset'] = PrescriptionFormSet(self.request.POST)
        else:
            context['prescription_formset'] = PrescriptionFormSet()
        context['appointment'] = get_object_or_404(Appointment, pk=self.kwargs['appointment_id'])
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        prescription_formset = context['prescription_formset']
        appointment = context['appointment']

        with transaction.atomic():
            form.instance.appointment = appointment
            form.instance.doctor = self.request.user
            self.object = form.save()

            if prescription_formset.is_valid():
                prescription_formset.instance = self.object
                prescription_formset.save()
            else:
                return self.form_invalid(form)

            # Update appointment status
            appointment.status = 'completed'
            appointment.save()

        messages.success(self.request, 'Examination record created successfully.')
        return redirect('examination_detail', pk=self.object.pk)

class ExaminationDetailView(LoginRequiredMixin, IsDoctorMixin, DetailView):
    model = Examination
    template_name = 'examinations/examination_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prescriptions'] = self.object.prescription_set.all()
        return context

class ExaminationUpdateView(LoginRequiredMixin, IsDoctorMixin, UpdateView):
    model = Examination
    form_class = ExaminationForm
    template_name = 'examinations/examination_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['prescription_formset'] = PrescriptionFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['prescription_formset'] = PrescriptionFormSet(instance=self.object)
        context['appointment'] = self.object.appointment
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        prescription_formset = context['prescription_formset']

        with transaction.atomic():
            self.object = form.save()
            if prescription_formset.is_valid():
                prescription_formset.instance = self.object
                prescription_formset.save()
            else:
                return self.form_invalid(form)

        messages.success(self.request, 'Examination record updated successfully.')
        return redirect('examination_detail', pk=self.object.pk)

User = get_user_model()

class SecretaryListView(LoginRequiredMixin, IsDoctorMixin, ListView):
    model = User
    template_name = 'secretary/secretary_list.html'
    context_object_name = 'secretaries'

    def get_queryset(self):
        return User.objects.filter(role='secretary')

class SecretaryCreateView(LoginRequiredMixin, IsDoctorMixin, CreateView):
    model = User
    form_class = SecretaryForm
    template_name = 'secretary/secretary_form.html'
    success_url = reverse_lazy('secretary_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = 'secretary'
        user.save()
        messages.success(self.request, 'Secretary account created successfully.')
        return super().form_valid(form)

class SecretaryUpdateView(LoginRequiredMixin, IsDoctorMixin, UpdateView):
    model = User
    form_class = SecretaryForm
    template_name = 'secretary/secretary_form.html'
    success_url = reverse_lazy('secretary_list')

    def get_queryset(self):
        return User.objects.filter(role='secretary')

    def form_valid(self, form):
        messages.success(self.request, 'Secretary account updated successfully.')
        return super().form_valid(form)

class SecretaryDeleteView(LoginRequiredMixin, IsDoctorMixin, DeleteView):
    model = User
    template_name = 'secretary/secretary_confirm_delete.html'
    success_url = reverse_lazy('secretary_list')

    def get_queryset(self):
        return User.objects.filter(role='secretary')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Secretary account deleted successfully.')
        return super().delete(request, *args, **kwargs)

# def dashboard(request):
#     today = timezone.now().date()
#     today_appointments = Appointment.objects.filter(date=today).order_by('time')
#     # ... rest of the view code ...
#     return render(request, 'dashboard.html', {'today_appointments': today_appointments})


class MedicineCreateView(CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/medicine_form.html'
    success_url = reverse_lazy('medicine_list')

class MedicineUpdateView(UpdateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/medicine_form.html'
    success_url = reverse_lazy('medicine_list')