from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Patient URLs
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/new/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    
    # Medicine URLs (Doctor Only)
    path('medicines/', views.MedicineListView.as_view(), name='medicine_list'),
    path('medicines/<int:pk>/', views.MedicineDetailView.as_view(), name='medicine_detail'),
    path('medicines/new/', views.MedicineCreateView.as_view(), name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.MedicineUpdateView.as_view(), name='medicine_update'),
    path('medicines/<int:pk>/delete/', views.MedicineDeleteView.as_view(), name='medicine_delete'),
    
    # Doctor Busy Hours URLs
    path('busy-hours/', views.DoctorBusyHoursListView.as_view(), name='busy_hours'),
    path('busy-hours/new/', views.DoctorBusyHoursCreateView.as_view(), name='busy_hours_create'),
    path('busy-hours/<int:pk>/edit/', views.DoctorBusyHoursUpdateView.as_view(), name='busy_hours_update'),
    path('busy-hours/<int:pk>/delete/', views.DoctorBusyHoursDeleteView.as_view(), name='busy_hours_delete'),
    
    # Examination URLs
    path('examinations/new/<int:appointment_id>/', views.ExaminationCreateView.as_view(), name='examination_create'),
    path('examinations/<int:pk>/', views.ExaminationDetailView.as_view(), name='examination_detail'),
    path('examinations/<int:pk>/edit/', views.ExaminationUpdateView.as_view(), name='examination_update'),
    path('api/calendar-events/', views.calendar_events, name='calendar_events'),
    
    # Secretary URLs
    path('secretaries/', views.SecretaryListView.as_view(), name='secretary_list'),
    path('secretaries/new/', views.SecretaryCreateView.as_view(), name='secretary_create'),
    path('secretaries/<int:pk>/edit/', views.SecretaryUpdateView.as_view(), name='secretary_update'),
    path('secretaries/<int:pk>/delete/', views.SecretaryDeleteView.as_view(), name='secretary_delete'),
]


