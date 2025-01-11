from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'index.html')


def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard.html', context)


def doctor(request):
    context = {
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
    }
    return render(request, 'doctor.html', context)


def staff(request):
    context = {
        'page_title': 'Staff Management',
        'active_page': 'staff',
    }
    return render(request, 'staff.html', context)


def patient(request):
    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
    }
    return render(request, 'patient.html', context)


def appointment(request):
    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
    }
    return render(request, 'appointment.html', context)


def schedule(request):
    context = {
        'page_title': 'Schedule Management',
        'active_page': 'schedule',
    }
    return render(request, 'schedule.html', context)


def finance(request):
    context = {
        'page_title': 'Finance Management',
        'active_page': 'finance',
    }
    return render(request, 'finance.html', context)


def statistics(request):
    context = {
        'page_title': 'Statistics',
        'active_page': 'statistics',
    }
    return render(request, 'statistics.html', context)
