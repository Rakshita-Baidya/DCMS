from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import dashboard, doctor, view_doctor_profile, edit_doctor_profile, staff, view_staff_profile, edit_staff_profile, patient, view_patient_profile, appointment, add_appointment, finance, statistics,  error, schedule
from .views import PatientFormWizard, EditPatientFormWizard

app_name = 'core'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),

    path('doctor/', doctor, name='doctor'),
    path('doctor/<int:user_id>/', view_doctor_profile, name='view_doctor_profile'),
    path('doctor/<int:user_id>/edit',
         edit_doctor_profile, name='edit_doctor_profile'),

    path('staff/', staff, name='staff'),
    path('staff/<int:user_id>/', view_staff_profile, name='view_staff_profile'),
    path('staff/<int:user_id>/edit', edit_staff_profile, name='edit_staff_profile'),


    path('patient/', patient, name='patient'),
    path('patient/<int:patient_id>/', view_patient_profile,
         name='view_patient_profile'),
    path('patient/add/', PatientFormWizard.as_view(), name='add_patient'),
    path('edit-patient/<int:patient_id>/',
         EditPatientFormWizard.as_view(), name='edit_patient_profile'),


    path('appointment/', appointment, name='appointment'),
    path('appointment/add/', add_appointment, name='add_appointment'),


    path('schedule/', schedule, name='schedule'),

    path('finance/', finance, name='finance',),
    path('statistics/', statistics, name='statistics'),

    path('error/', error, name='error')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
