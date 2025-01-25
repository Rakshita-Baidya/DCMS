from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import Staff

# Create your views here.


def home(request):
    return render(request, 'index.html')


def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard/dashboard.html', context)


def doctor(request):
    context = {
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
    }
    return render(request, 'doctor/doctor.html', context)


def staff(request):
    staff_queryset = Staff.objects.all()

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        staff_queryset = staff_queryset.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(staff_queryset, 10)
    page = request.GET.get('page', 1)
    staff_list = paginator.get_page(page)

    context = {
        'page_title': 'Staff Management',
        'active_page': 'staff',
        'staff': staff_list,
        'total_staff': staff_queryset.count(),
        'search_query': search_query,
    }
    
    return render(request, 'staff/staff.html', context)


def patient(request):
    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
    }
    return render(request, 'patient/patient.html', context)


def appointment(request):
    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
    }
    return render(request, 'appointment/appointment.html', context)


def schedule(request):
    context = {
        'page_title': 'Schedule Management',
        'active_page': 'schedule',
    }
    return render(request, 'schedule/schedule.html', context)


def finance(request):
    context = {
        'page_title': 'Finance Management',
        'active_page': 'finance',
    }
    return render(request, 'finance/finance.html', context)


def statistics(request):
    context = {
        'page_title': 'Statistics',
        'active_page': 'statistics',
    }
    return render(request, 'statistics/statistics.html', context)
