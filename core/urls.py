from django.urls import path
from .views import dashboard, doctor, schedule, staff, patient, appointment, finance, statistics, view_staff_profile, edit_staff_profile, view_doctor_profile, edit_doctor_profile, error

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
    path('appointment/', appointment, name='appointment'),
    path('schedule/', schedule, name='schedule'),

    path('finance/', finance, name='finance',),
    path('statistics/', statistics, name='statistics'),

    path('error/', error, name='error')
]
