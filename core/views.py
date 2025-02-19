from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import admin_only, allowed_users, unauthenticated_user
from django.core.files.storage import FileSystemStorage
import os
from django.forms import formset_factory

from formtools.wizard.views import SessionWizardView
from django.urls import reverse

from users.models import Staff, User, Doctor
from users.forms import StaffForm, DoctorForm, UserEditForm

from .models import (Patient, MedicalHistory, OtherPatientHistory, DentalChart,
                     ToothRecord, Transaction, Appointment, Treatment, TreatmentDoctor, PurchasedProduct)
from .forms import (AppointmentForm, PatientForm,  MedicalHistoryForm,
                    OtherPatientHistoryForm, DentalChartForm, PurchasedProductFormSet, ToothRecordFormSet, TreatmentDoctorForm, TreatmentDoctorFormSet, TreatmentForm)


# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    patient_queryset = Patient.objects.all().order_by('id')

    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'total_patient': patient_queryset.count(),
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
    patient_queryset = Patient.objects.all().order_by('id')

    # patient needs to be deleted
    if request.method == 'POST' and 'delete_patient_id' in request.POST:
        patient_id_to_delete = request.POST['delete_patient_id']
        patient_to_delete = Patient.objects.get(id=patient_id_to_delete)
        patient_to_delete.delete()
        messages.success(request, f"Patient {
                         patient_to_delete.name} has been deleted.")

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


class PatientFormWizard(SessionWizardView):
    form_list = [PatientForm, MedicalHistoryForm,
                 OtherPatientHistoryForm, DentalChartForm]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "patient"))

    TEMPLATES = {
        "0": "patient/general.html",
        "1": "patient/history.html",
        "2": "patient/other.html",
        '3': 'patient/dental_chart.html',
    }

    def get_template_names(self):
        return [self.TEMPLATES.get(str(self.steps.current), "patient/general.html")]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        # context['profile_image'] = self.request.session.get('profile_image')
        context.update({
            'page_title': 'Patient Management',
            'active_page': 'patient',
        })
        if self.steps.current == '3':  # Dental Chart step
            context['tooth_record_formset'] = ToothRecordFormSet()
        return context

    def get_form_instance(self, step):
        if step == '0':  # Patient Form
            return Patient()
        elif step == '1':  # Medical History Form
            return MedicalHistory()
        elif step == '2':  # remaining
            return OtherPatientHistory()
        elif step == '3':  # Dental Chart Form
            return DentalChart()
        return None

    def done(self, form_list, **kwargs):
        request = self.request
        # Save patient info
        patient = form_list[0].save()

        # if 'profile_image' in request.session:
        #     patient.profile_image = request.session['profile_image']
        #     patient.save()

        # Save medical history
        medical_history = form_list[1].save(commit=False)
        medical_history.patient = patient
        medical_history.save()

        # Save other history
        other_history = form_list[2].save(commit=False)
        other_history.history = medical_history
        other_history.save()

        # Save dental chart
        dental_chart = form_list[3].save(commit=False)
        dental_chart.patient = patient
        dental_chart.save()

        # Save tooth records
        tooth_record_formset = ToothRecordFormSet(
            request.POST, instance=dental_chart)
        if tooth_record_formset.is_valid():
            tooth_record_formset.save()

        messages.success(request, 'The patient has been added successfully!')
        return redirect('core:patient')


class EditPatientFormWizard(SessionWizardView):
    form_list = [PatientForm, MedicalHistoryForm,
                 OtherPatientHistoryForm, DentalChartForm]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "patient"))

    TEMPLATES = {
        "0": "patient/general.html",
        "1": "patient/history.html",
        "2": "patient/other.html",
        '3': 'patient/dental_chart.html',
    }

    def get_template_names(self):
        return [self.TEMPLATES.get(str(self.steps.current), "patient/general.html")]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        patient_id = self.kwargs.get('patient_id')
        context.update({
            'page_title': 'Patient Management',
            'active_page': 'patient',
            'is_editing': bool(patient_id),
        })
        if self.steps.current == '3':  # Dental Chart step
            dental_chart = self.get_form_instance('3')
            context['tooth_record_formset'] = ToothRecordFormSet(
                instance=dental_chart)

        return context

    def get_form_instance(self, step):
        patient_id = self.kwargs.get('patient_id')
        if not patient_id:
            return None

        patient = get_object_or_404(Patient, id=patient_id)

        if step == '0':  # Patient Form
            return patient
        elif step == '1':  # Medical History Form
            medical_history, created = MedicalHistory.objects.get_or_create(
                patient=patient)

            return medical_history
        elif step == '2':
            medical_history, created = MedicalHistory.objects.get_or_create(
                patient=patient)
            other_history, created = OtherPatientHistory.objects.get_or_create(
                history=medical_history)
            # Add this debug line
            print("Retrieved date:", other_history.date_of_last_extraction)

            return other_history
        elif step == '3':  # Dental Chart Form
            dental_chart, created = DentalChart.objects.get_or_create(
                patient=patient)
            return dental_chart
        return None

    def done(self, form_list, **kwargs):
        request = self.request
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)

        # Update patient info
        patient_form = form_list[0]
        for field, value in patient_form.cleaned_data.items():
            setattr(patient, field, value)
        patient.save()

        # Update or create medical history
        medical_history_form = form_list[1]
        medical_history, created = MedicalHistory.objects.update_or_create(
            patient=patient, defaults=medical_history_form.cleaned_data
        )

        # Update or create other patient history
        other_history_form = form_list[2]
        OtherPatientHistory.objects.update_or_create(
            history=medical_history, defaults=other_history_form.cleaned_data
        )

        # Update or create dental chart
        dental_chart_form = form_list[3]
        dental_chart, created = DentalChart.objects.update_or_create(
            patient=patient, defaults=dental_chart_form.cleaned_data
        )

        # Update or create tooth records
        tooth_record_formset = ToothRecordFormSet(
            request.POST, instance=dental_chart)
        if tooth_record_formset.is_valid():
            tooth_record_formset.save()

        messages.success(
            request, 'The patient details have been updated successfully!')
        return redirect('core:patient')


@login_required(login_url='login')
def view_patient_profile(request, patient_id):
    patient_queryset = Patient.objects.get(pk=patient_id)

    patient_history = getattr(patient_queryset, 'patient_history', None)
    history_other_patients = getattr(
        patient_history, 'history_other_patients', None)
    dental_chart = getattr(patient_queryset, 'dental_chart')

    exclude_fields = {'id', 'patient', 'history'}

    # Define sections for medical history
    medical_history_sections = {
        "General": ["chief_dental_complaint", "marked_weight_change"],
        "Heart": ["chest_pain", "hypertention", "ankle_edema", "rheumatic_fever", "rheumatic_fever_age", "stroke_history", "stroke_date"],
        "Arthritis": ["joint_pain", "joint_swelling"],
        "Nervous System": ["headaches", "convulsions_or_epilepsy", "numbness_or_tingles", "dizziness_or_fainting"],
        "Liver": ["jaundice", "history_of_liver_disease", "liver_disease_specifics"],
        "Women": ["pregnancy", "pregnancy_month", "breast_feed"],
        "Respiratory": ["persistant_cough", "breathing_difficulty", "shortness_of_breath", "asthma"],
        "Ear": ["hearing_loss", "ringing_of_ears"],
        "Blood": ["bruise_easy", "anemia"],
        "Thyroid": ["perspire_easy", "apprehension", "palpitation", "goiter", "bulging_eyes"],
        "Diabetes": ["delayed_healing", "increased_appetite", "family_history"],
        "Radiography": ["radiography_therapy"],
        "Urinary": ["increased_frequency", "burning"],
    }

    # Define sections for other patient history
    other_history_sections = {
        "Extraction": ["prev_extraction", "date_of_last_extraction", "untoward_reaction", "untoward_reaction_specifics", "local_anesthesia_use"],
        "Hospitalization": ["hospitalized", "admission_date", "hospitalization_specifics"],
        "Allergies": ["sleeping_pills", "aspirin", "food", "penicilin", "antibiotics", "sulfa_drugs", "local_anesthesia", "others", "specifics"],
    }

    def get_sectioned_data(instance, sections):
        data = {}
        if instance:
            for section, fields in sections.items():
                section_data = {field: getattr(
                    instance, field) for field in fields if getattr(instance, field)}
                if section_data:
                    data[section] = section_data
        return data

    medical_history_data = get_sectioned_data(
        patient_history, medical_history_sections)
    other_history_data = get_sectioned_data(
        history_other_patients, other_history_sections)

    # patient needs to be deleted
    if request.method == 'POST' and 'delete_patient_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            patient_id_to_delete = request.POST['delete_patient_id']
            patient_to_delete = Patient.objects.get(id=patient_id_to_delete)
            patient_to_delete.delete()
            messages.success(request, f"Patient {
                patient_to_delete.name} has been deleted.")
            return redirect('core:patient')

    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
        'patient': patient_queryset,
        'medical_history_data': medical_history_data,
        'other_history_data': other_history_data,
        'dental_chart': dental_chart,
        'tooth_records': dental_chart.tooth_records.all() if dental_chart else None,
    }

    return render(request, 'patient/view_patient_profile.html', context)


@login_required(login_url='login')
def appointment(request):
    appointment_queryset = Appointment.objects.all().order_by('id')

    # appointment needs to be deleted
    if request.method == 'POST' and 'delete_appointment_id' in request.POST:
        appointment_id_to_delete = request.POST['delete_appointment_id']
        appointment_to_delete = Appointment.objects.get(
            id=appointment_id_to_delete)
        appointment_to_delete.delete()
        messages.success(request, f"Appointment for {
                         appointment_to_delete.patient.name} on {appointment_to_delete.date} at {appointment_to_delete.time} has been deleted.")

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        appointment_queryset = appointment_queryset.filter(
            Q(patient__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(appointment_queryset, 8)
    page = request.GET.get('page', 1)
    appointment_list = paginator.get_page(page)

    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
        'appointments': appointment_list,
        'total_appointment': appointment_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'appointment/appointment.html', context)


# def add_appointment(request):
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             appointment = form.save(commit=False)
#             appointment.save()
#             messages.success(
#                 request, 'The appointment has been scheduled successfully!')
#             return redirect('core:appointment')
#     else:
#         form = AppointmentForm()

#     context = {
#         'page_title': 'Appointment Management',
#         'active_page': 'appointment',
#         'form': form,
#     }
#     return render(request, 'appointment/add_appointment.html', context)


class AppointmentFormWizard(SessionWizardView):
    form_list = [AppointmentForm, TreatmentForm,
                 TreatmentDoctorForm, PurchasedProductFormSet]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "appointment"))

    TEMPLATES = {
        '0': 'appointment/add_appointment.html',
        '1': 'appointment/add_treatment.html',
        '2': 'appointment/add_treatment_doctor.html',
        '3': 'appointment/add_purchased_product.html',
    }

    def get_template_names(self):
        return [self.TEMPLATES.get(str(self.steps.current), "appointment/add_appointment.html")]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context.update({
            'page_title': 'Appointment Management',
            'active_page': 'appointment',
            'patients': Patient.objects.all(),
            'doctors': User.objects.filter(role='Doctor', doctor_profile__isnull=False)

        })
        if self.steps.current == '2':
            context['treatment_doctor_formset'] = TreatmentDoctorFormSet()
        if self.steps.current == '3':
            context['purchased_product_formset'] = PurchasedProductFormSet()
        return context

    def get_form_instance(self, step):
        if step == '0':
            return Appointment()
        elif step == '1':
            return Treatment()
        elif step == '2':
            return TreatmentDoctor()
        elif step == '3':
            return PurchasedProduct()
        return None

    def done(self, form_list, **kwargs):
        request = self.request

        appointment = form_list[0].save()

        treatment = form_list[1].save(commit=False)
        treatment.appointment = appointment
        treatment.save()

        treatment_doctor = form_list[2].save(commit=False)
        treatment_doctor.treatment = treatment
        treatment_doctor.save()

        purchased_product = form_list[3].save(commit=False)
        purchased_product.appointment = appointment
        purchased_product.save()

        treatment_doctor_formset = TreatmentDoctorFormSet(
            request.POST, instance=treatment_doctor)
        if treatment_doctor_formset.is_valid():
            treatment_doctor_formset.save()

        purchased_product_formset = PurchasedProductFormSet(
            request.POST, instance=purchased_product)
        if purchased_product_formset.is_valid():
            purchased_product_formset.save()

        messages.success(
            request, 'The appointment has been added successfully!')
        return redirect('core:appointment')


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
