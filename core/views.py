from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import admin_only, allowed_users, unauthenticated_user
from django.core.files.storage import FileSystemStorage
import os

from formtools.wizard.views import SessionWizardView
from django.urls import reverse

from users.models import Staff, User, Doctor
from users.forms import StaffForm, DoctorForm, UserEditForm

from .models import (Patient, MedicalHistory, HeartHistory, HospitalizationHistory, EarHistory, EmergencyContact, ArthritisHistory, NervousHistory, WomenHistory,
                     LiverHistory, RadiographyHistory, RespitoryHistory, ExtractionHistory, BloodHistory, AllergiesHistory, DiabetesHistory, ThyroidHistory, UrinaryHistory)
from .forms import (PatientForm, EmergencyContactForm, MedicalHistoryForm, HeartHistoryForm, HospitalizationHistoryForm, EarHistoryForm, ArthritisHistoryForm, EarHistoryForm, EmergencyContactForm, ArthritisHistoryForm,
                    NervousHistoryForm, WomenHistoryForm, LiverHistoryForm, RadiographyHistoryForm, RespitoryHistoryForm, ExtractionHistoryForm, BloodHistoryForm, AllergiesHistoryForm, DiabetesHistoryForm, ThyroidHistoryForm, UrinaryHistoryForm)


# Create your views here.
FORMS = [
    # general
    ("general", PatientForm),
    ("emergency", EmergencyContactForm),

    # history
    ("medical", MedicalHistoryForm),
    ("blood", BloodHistoryForm),
    ("diabetes", DiabetesHistoryForm),
    ("thyroid", ThyroidHistoryForm),
    ("urinary", UrinaryHistoryForm),
    ("heart", HeartHistoryForm),
    ("liver", LiverHistoryForm),
    ("radiography", RadiographyHistoryForm),
    ("respiratory", RespitoryHistoryForm),
    ("nervous", NervousHistoryForm),
    ("women", WomenHistoryForm),
    ("arthritis", ArthritisHistoryForm),
    ("ear", EarHistoryForm),

    # allergies
    ("allergies", AllergiesHistoryForm),
    ("hospitalization", HospitalizationHistoryForm),
    ("extraction", ExtractionHistoryForm),
]

TEMPLATES = {
    "general": "patient/general.html",
    "history": "patient/history.html",
    "allergies": "patient/allergies.html",
}

file_storage = FileSystemStorage(
    location=os.path.join("media", "wizard_uploads"))

# def home(request):
#     return render(request, 'index.html')


@login_required(login_url='login')
def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
def doctor(request):
    doctor_queryset = Doctor.objects.all()

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        doctor_queryset = doctor_queryset.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(doctor_queryset, 8)
    page = request.GET.get('page', 1)
    doctor_list = paginator.get_page(page)

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:doctor')

    context = {
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
        'doctor': doctor_list,
        'total_doctor': doctor_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'doctor/doctor.html', context)


@login_required(login_url='login')
def view_doctor_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    doctor_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'Doctor' and hasattr(user_queryset, 'doctor_profile'):
        doctor_profile = user_queryset.doctor_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:doctor')

    context = {
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
        'user': user_queryset,
        'doctor_profile': doctor_profile,
    }

    return render(request, 'doctor/view_doctor_profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Doctor', 'Administrator'])
def edit_doctor_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    doctor_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'Doctor' and hasattr(user_queryset, 'doctor_profile'):
        doctor_profile = user_queryset.doctor_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:doctor')

    if request.method == 'POST':
        user_form = UserEditForm(
            request.POST, request.FILES, instance=user_queryset)
        doctor_form = DoctorForm(
            request.POST, instance=doctor_profile) if doctor_profile else None

        if user_form.is_valid():
            user_form.save()
            if doctor_form and doctor_form.is_valid():
                doctor_form.save()

            messages.success(
                request, 'The doctor profile has been updated successfully!')
            return redirect('core:view_doctor_profile', user_id=user_queryset.id)
    else:
        user_form = UserEditForm(instance=user_queryset)
        doctor_form = DoctorForm(
            instance=doctor_profile) if doctor_profile else None

    context = {
        'user': user_queryset,
        'user_form': user_form,
        'doctor_form': doctor_form,
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
    }

    return render(request, 'doctor/edit_doctor_profile.html', context)


@login_required(login_url='login')
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

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:staff')

    context = {
        'page_title': 'Staff Management',
        'active_page': 'staff',
        'staff': staff_list,
        'total_staff': staff_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'staff/staff.html', context)


@login_required(login_url='login')
def view_staff_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    staff_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'Staff' and hasattr(user_queryset, 'staff_profile'):
        staff_profile = user_queryset.staff_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:staff')

    context = {
        'page_title': 'Staff Management',
        'active_page': 'staff',
        'user': user_queryset,
        'staff_profile': staff_profile,
    }

    return render(request, 'staff/view_staff_profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Staff', 'Administrator'])
def edit_staff_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    staff_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'Staff' and hasattr(user_queryset, 'staff_profile'):
        staff_profile = user_queryset.staff_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('core:staff')

    if request.method == 'POST':
        user_form = UserEditForm(
            request.POST, request.FILES, instance=user_queryset)
        staff_form = StaffForm(
            request.POST, instance=staff_profile) if staff_profile else None

        if user_form.is_valid():
            user_form.save()
            if staff_form and staff_form.is_valid():
                staff_form.save()

            messages.success(
                request, 'The staff profile has been updated successfully!')
            return redirect('core:view_staff_profile', user_id=user_queryset.id)
    else:
        user_form = UserEditForm(instance=user_queryset)
        staff_form = StaffForm(
            instance=staff_profile) if staff_profile else None

    context = {
        'user': user_queryset,
        'user_form': user_form,
        'staff_form': staff_form,
        'page_title': 'Staff Management',
        'active_page': 'staff',
    }

    return render(request, 'staff/edit_staff_profile.html', context)


@login_required(login_url='login')
def patient(request):

    # Allow only superusers and admins
    # if not request.user.is_superuser and request.user.role != 'Administrator':
    #     messages.error(request, "Access denied.")
    #     return redirect('login')
    # else:
    patient_queryset = Patient.objects.all().order_by('reg_no')

    # patient needs to be deleted
    if request.method == 'POST' and 'delete_patient_id' in request.POST:
        patient_id_to_delete = request.POST['delete_patient_id']
        patient_to_delete = Patient.objects.get(id=patient_id_to_delete)
        patient_to_delete.delete()
        messages.success(request, f"Patient {
                         patient_to_delete.patientname} has been deleted.")

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        patient_queryset = patient_queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(patient_queryset, 8)
    page = request.GET.get('page', 1)
    patient_list = paginator.get_page(page)

    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
        'patients': patient_list,
        'total_patient': patient_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'patient/patient.html', context)


# def add_patient(request):
#     if request.method == 'POST':
#         form = PatientForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request, 'The patient has been added successfully!')
#             return redirect('core:patient')
#     else:
#         form = PatientForm()

#     context = {
#         'page_title': 'Patient Management',
#         'active_page': 'patient',
#         'form': form,

#     }

#     return render(request, 'patient/add_patient.html', context)

class PatientWizard(SessionWizardView):
    form_list = FORMS
    file_storage = file_storage

    def get_template_names(self):
        """Determine which template to use based on the current step."""
        general_forms = {"general", "emergency"}
        history_forms = {
            "medical", "blood", "diabetes", "thyroid", "urinary",
            "heart", "liver", "radiography", "respiratory", "nervous",
            "women", "arthritis", "ear"
        }
        allergies_forms = {"allergies", "hospitalization", "extraction"}

        if self.steps.current in general_forms:
            return [TEMPLATES["general"]]
        elif self.steps.current in history_forms:
            return [TEMPLATES["history"]]
        elif self.steps.current in allergies_forms:
            return [TEMPLATES["allergies"]]

        return [TEMPLATES["general"]]  # Default fallback

    def done(self, form_list, **kwargs):
        form_data = {form.prefix: form.cleaned_data for form in form_list}

        # Save the Patient and Emergency
        general_data = form_data.get("general", {})
        emergency_data = form_data.get("emergency", {})

        patient_instance = Patient.objects.create(**general_data)
        EmergencyContact.objects.create(
            patient=patient_instance, **emergency_data)

        # Save History-related data
        history_models = {
            "medical": MedicalHistory,
            "blood": BloodHistory,
            "diabetes": DiabetesHistory,
            "thyroid": ThyroidHistory,
            "urinary": UrinaryHistory,
            "heart": HeartHistory,
            "liver": LiverHistory,
            "radiography": RadiographyHistory,
            "respiratory": RespitoryHistory,
            "nervous": NervousHistory,
            "women": WomenHistory,
            "arthritis": ArthritisHistory,
            "ear": EarHistory,
        }

        for key, model in history_models.items():
            if key in form_data:
                model.objects.create(
                    patient=patient_instance, **form_data[key])

        # Save Allergies-related data
        allergies_models = {
            "allergies": AllergiesHistory,
            "hospitalization": HospitalizationHistory,
            "extraction": ExtractionHistory,
        }

        for key, model in allergies_models.items():
            if key in form_data:
                model.objects.create(
                    patient=patient_instance, **form_data[key])

        messages.success(self.request, "Patient added successfully!")
        return redirect("core:patient")


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


@login_required(login_url='login')
@admin_only
def finance(request):
    context = {
        'page_title': 'Finance Management',
        'active_page': 'finance',
    }
    return render(request, 'finance/finance.html', context)


@login_required(login_url='login')
@admin_only
def statistics(request):
    context = {
        'page_title': 'Statistics',
        'active_page': 'statistics',
    }
    return render(request, 'statistics/statistics.html', context)


def error(request):
    return render(request, 'error.html')
