from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import dashboard, doctor, schedule, staff, patient, appointment, finance, statistics, view_staff_profile, edit_staff_profile, view_doctor_profile, edit_doctor_profile, error, edit_patient_profile
from .views import PatientFormWizard

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
    # path('patient/add/', add_patient, name='add_patient'),
    #     path('patient/add/', PatientWizard.as_view(), name='add_patient'),
    path('patient/add/', PatientFormWizard.as_view(), name='add_patient'),
    path('patient/<int:patient_id>/edit',
         edit_patient_profile, name='edit_patient_profile'),

    path('appointment/', appointment, name='appointment'),
    path('schedule/', schedule, name='schedule'),

    path('finance/', finance, name='finance',),
    path('statistics/', statistics, name='statistics'),

    path('error/', error, name='error')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
