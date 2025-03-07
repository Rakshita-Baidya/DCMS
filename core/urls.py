from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (dashboard, doctor, view_doctor_profile, edit_doctor_profile, staff, view_staff_profile, edit_staff_profile,
                    patient, view_patient_profile, appointment, view_appointment, finance, statistics,  error, schedule, edit_patient_profile)
from .views import PatientFormWizard, EditPatientFormWizard, AppointmentFormWizard, EditAppointmentWizard

from .views import (
    PatientViewSet, MedicalHistoryViewSet, OtherPatientHistoryViewSet,
    DentalChartViewSet, ToothRecordViewSet, AppointmentViewSet,
    TreatmentPlanViewSet, TreatmentRecordViewSet, TreatmentDoctorViewSet,
    PurchasedProductViewSet, PaymentViewSet, TransactionViewSet
)

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
    path('patient/<int:patient_id>/edit/<int:step>/',
         edit_patient_profile, name='edit_patient_profile_step'),


    path('appointment/', appointment, name='appointment'),
    #     path('appointment/add/', add_appointment, name='add_appointment'),
    path('appointment/add/', AppointmentFormWizard.as_view(), name='add_appointment'),
    path('edit-appointment/<int:appointment_id>/',
         EditAppointmentWizard.as_view(), name='edit_appointment'),
    path('appointment/<int:appointment_id>/view/',
         view_appointment, name='view_appointment'),

    path('schedule/', schedule, name='schedule'),

    path('finance/', finance, name='finance',),
    path('statistics/', statistics, name='statistics'),

    path('error/', error, name='error'),


    #     api urls
    # Patient URLs
    path('patients/list/',
         PatientViewSet.as_view({'get': 'list'}), name='patient_list'),
    path('patients/<int:pk>/', PatientViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='patient'),

    # Medical History URLs
    path('medical-histories/list/', MedicalHistoryViewSet.as_view({
        'get': 'list'
    }), name='medical_history_list'),
    path('medical-histories/<int:pk>/', MedicalHistoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='medical_history'),

    # Other Patient History URLs
    path('other-patient-histories/list/', OtherPatientHistoryViewSet.as_view({
        'get': 'list'
    }), name='other_patient_history_list'),
    path('other-patient-histories/<int:pk>/', OtherPatientHistoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='other_patient_history'),

    # Dental Chart URLs
    path('dental-charts/list/', DentalChartViewSet.as_view({
        'get': 'list'
    }), name='dental_chart_list'),
    path('dental-charts/<int:pk>/', DentalChartViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='dental_chart'),

    # Tooth Record URLs
    path('tooth-records/list/', ToothRecordViewSet.as_view({
        'get': 'list'
    }), name='tooth_record_list'),
    path('tooth-records/<int:pk>/', ToothRecordViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='tooth_record'),

    # Appointment URLs
    path('appointments/list/', AppointmentViewSet.as_view({
        'get': 'list'
    }), name='appointment_list'),
    path('appointments/<int:pk>/', AppointmentViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='appointment'),

    # Treatment Plan URLs
    path('treatment-plans/list/', TreatmentPlanViewSet.as_view({
        'get': 'list'
    }), name='treatment_plan_list'),
    path('treatment-plans/<int:pk>/', TreatmentPlanViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='treatment_plan'),

    # Treatment Record URLs
    path('treatment-records/list/', TreatmentRecordViewSet.as_view({
        'get': 'list'
    }), name='treatment_record_list'),
    path('treatment-records/<int:pk>/', TreatmentRecordViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='treatment_record'),

    # Treatment Doctor URLs
    path('treatment-doctors/list/', TreatmentDoctorViewSet.as_view({
        'get': 'list'
    }), name='treatment_doctor_list'),
    path('treatment-doctors/<int:pk>/', TreatmentDoctorViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='treatment_doctor'),

    # Purchased Product URLs
    path('purchased-products/list/', PurchasedProductViewSet.as_view({
        'get': 'list'
    }), name='purchased_product_list'),
    path('purchased-products/<int:pk>/', PurchasedProductViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='purchased_product'),

    # Payment URLs
    path('payments/list/', PaymentViewSet.as_view({
        'get': 'list'
    }), name='payment_list'),
    path('payments/<int:pk>/', PaymentViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='payment'),

    # Transaction URLs
    path('transactions/list/', TransactionViewSet.as_view({
        'get': 'list'
    }), name='transaction_list'),
    path('transactions/<int:pk>/', TransactionViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'create'
    }), name='transaction'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
