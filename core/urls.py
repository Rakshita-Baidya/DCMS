from django.urls import path
from .views import dashboard, doctor, schedule, staff, patient, appointment, finance, statistics

app_name = 'core'

urlpatterns = [

    path('dashboard/', dashboard, name='dashboard'),
    path('doctor/', doctor, name='doctor'),
    path('staff/', staff, name='staff'),
    path('patient/', patient, name='patient'),
    path('appointment/', appointment, name='appointment'),
    path('schedule/', schedule, name='schedule'),

    path('finance/', finance, name='finance',),
    path('statistics/', statistics, name='statistics')
]
