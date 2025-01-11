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
        'page_title': 'Doctor',
        'active_page': 'doctor',
    }
    return render(request, 'doctor.html', context)


def staff(request):
    context = {
        'page_title': 'Staff',
        'active_page': 'staff',
    }
    return render(request, 'staff.html', context)


def patient(request):
    context = {
        'page_title': 'Patient',
        'active_page': 'patient',
    }
    return render(request, 'patient.html', context)


def appointment(request):
    context = {
        'page_title': 'Appointment',
        'active_page': 'appointment',
    }
    return render(request, 'appointment.html', context)


def schedule(request):
    context = {
        'page_title': 'Schedule',
        'active_page': 'schedule',
    }
    return render(request, 'schedule.html', context)
