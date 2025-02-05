from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import Staff, User, Doctor
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
    paginator = Paginator(staff_queryset, 8)
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


def view_staff_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    staff_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'staff' and hasattr(user_queryset, 'staff_profile'):
        staff_profile = user_queryset.staff_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'admin':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('view_user_profile')

    context = {
        'page_title': 'Staff Management',
        'active_page': 'staff',
        'user': user_queryset,
        'staff_profile': staff_profile,
    }

    return render(request, 'staff/view_staff_profile.html', context)


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
