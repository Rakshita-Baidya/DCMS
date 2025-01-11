from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctor/', views.doctor, name='doctor'),
    path('staff/', views.staff, name='staff'),
    path('patient/', views.patient, name='patient'),
    path('appointment/', views.appointment, name='appointment'),
    path('schedule/', views.schedule, name='schedule'),
]
