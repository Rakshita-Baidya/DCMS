from datetime import timedelta
from django.db.models import Count, Sum
from decimal import Decimal

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.forms import formset_factory
from django.utils import timezone

import os
from datetime import date, datetime, timedelta
import json
from formtools.wizard.views import SessionWizardView

from users.models import User
from users.forms import UserEditForm
from users.serializers import UserSerializer
from users.decorators import AdminOnly, AllowedUsers, UnauthenticatedUser

from .models import (Patient, MedicalHistory, DentalChart, Payment, ToothRecord, Appointment,
                     TreatmentPlan, TreatmentRecord, TreatmentDoctor, PurchasedProduct, Transaction)
from .forms import (AppointmentForm, PatientForm,  MedicalHistoryForm,
                    DentalChartForm, PaymentForm, PurchasedProductFormSet, ToothRecordFormSet, TransactionForm, TreatmentDoctorForm, TreatmentDoctorFormSet, TreatmentPlanForm, TreatmentRecordForm)

from .serializers import (PatientSerializer, MedicalHistorySerializer,  AppointmentSerializer, ToothRecordSerializer, DentalChartSerializer,
                          PaymentSerializer, TransactionSerializer, TreatmentPlanSerializer, TreatmentDoctorSerializer, TreatmentRecordSerializer, PurchasedProductSerializer)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

# Create your views here.


@login_required(login_url='login')
def dashboard(request):
    time_filter = request.GET.get('filter', 'monthly')
    today = timezone.now().date()
    apply_date_filter = True

    # Initialize querysets
    patient_queryset = Patient.objects.all().order_by('id')
    appointments = Appointment.objects.all().order_by('-status')
    treatment_queryset = TreatmentRecord.objects.all()

    # Define date range based on time_filter
    start_date = None
    end_date = today

    if time_filter == 'overall':
        apply_date_filter = False
    elif time_filter == 'daily':
        start_date = today
    elif time_filter == 'weekly':
        days_since_sunday = (today.weekday() + 1) % 7
        start_date = today - timedelta(days=days_since_sunday)
    elif time_filter == 'monthly':
        start_date = today.replace(day=1)
    elif time_filter == 'quarterly':
        start_date = today - timedelta(days=90)
    elif time_filter == 'yearly':
        start_date = today.replace(month=1, day=1)

    # Apply date filters only if needed
    if apply_date_filter and start_date:
        date_range = [start_date, end_date]
        appointments = appointments.filter(date__range=date_range)
        patient_queryset = patient_queryset.filter(
            date_created__date__range=date_range)
        treatment_queryset = treatment_queryset.filter(
            date_created__date__range=date_range)

    # Calculate counts
    pending_appointments = appointments.filter(status="Pending")
    lab_orders = treatment_queryset.filter(lab=True).count()
    x_rays_taken = treatment_queryset.filter(x_ray=True).count()

    # Serialize data
    serialized_appointments = AppointmentSerializer(
        appointments, many=True).data
    serialized_treatments = TreatmentRecordSerializer(
        treatment_queryset, many=True).data

    # Appointment status counts
    status_counts = {
        "Completed": appointments.filter(status="Completed").count(),
        "Pending": pending_appointments.count(),
        "Cancelled": appointments.filter(status="Cancelled").count(),
    }

    # Treatment counts
    treatment_types = [
        "Root Canals", "Dental Crowns", "Fillings", "Cleaning", "General Checkup",
        "Extractions", "Prosthetics", "Dental Implants", "Other"
    ]
    treatment_counts = {ttype: treatment_queryset.filter(
        treatment_type=ttype).count() for ttype in treatment_types}

    # Follow-ups
    two_weeks_later = today + timedelta(days=14)
    two_weeks_earlier = today - timedelta(days=14)
    follow_ups = []
    for appointment in Appointment.objects.filter(follow_up_days__isnull=False, status="Completed"):
        follow_up_date = appointment.get_follow_up_date()
        if follow_up_date and two_weeks_earlier <= follow_up_date <= two_weeks_later:
            follow_ups.append(appointment)

    follow_ups.sort(key=lambda x: x.get_follow_up_date() or today)

    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'total_patient': patient_queryset.count(),
        'appointments': appointments,
        'total_appointment': appointments.count(),
        'pending_appointments': pending_appointments,
        'appointment_data': json.dumps(status_counts),
        'follow_ups': follow_ups,
        'treatments': treatment_queryset,
        'treatment_data': json.dumps(treatment_counts),
        'lab_orders': lab_orders,
        'x_rays_taken': x_rays_taken,
        'time_filter': time_filter,

    }
    return render(request, 'dashboard/dashboard.html', context)


@AllowedUsers(allowed_roles=['Administrator'])
@login_required(login_url='login')
def doctor(request):
    doctor_queryset = User.objects.filter(
        role='Doctor').order_by('first_name')

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        doctor_queryset = doctor_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )

    # Add specialization filter
    specialization_filter = request.GET.get('specialization', '')
    if specialization_filter:
        doctor_queryset = doctor_queryset.filter(
            specialization__iexact=specialization_filter)

    # Get unique specializations for the filter dropdown
    specializations = User.objects.filter(role='Doctor').values_list(
        'specialization', flat=True).distinct()

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
        'specialization_filter': specialization_filter,
        'specializations': specializations,
    }

    return render(request, 'doctor/doctor.html', context)


@AllowedUsers(allowed_roles=['Administrator'])
@login_required(login_url='login')
def view_doctor_profile(request, user_id):
    doctor_queryset = User.objects.get(pk=user_id)

    appointments = Appointment.objects.filter(
        treatment_records__doctors__doctor=doctor_queryset).distinct().order_by('-date', '-time')[:5]
    treatment_queryset = TreatmentRecord.objects.filter(
        doctors__doctor=doctor_queryset
    )

    # Define treatment counts similar to dashboard
    treatment_counts = {
        "Root Canals": treatment_queryset.filter(treatment_type="Root Canals").count(),
        "Dental Crowns": treatment_queryset.filter(treatment_type="Dental Crowns").count(),
        "Fillings": treatment_queryset.filter(treatment_type="Fillings").count(),
        "Cleaning": treatment_queryset.filter(treatment_type="Cleaning").count(),
        "General Checkup": treatment_queryset.filter(treatment_type="General Checkup").count(),
        "Extractions": treatment_queryset.filter(treatment_type="Extractions").count(),
        "Prosthetics": treatment_queryset.filter(treatment_type="Prosthetics").count(),
        "Dental Implants": treatment_queryset.filter(treatment_type="Dental Implants").count(),
        "Other": treatment_queryset.filter(treatment_type="Other").count(),
    }

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
        'doctor': doctor_queryset,
        'appointments': appointments,
        'treatment_data': json.dumps(treatment_counts),
    }

    return render(request, 'doctor/view_doctor_profile.html', context)


@login_required(login_url='login')
@AllowedUsers(allowed_roles=['Administrator'])
def edit_doctor_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)

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

        if user_form.is_valid():
            user_form.save()

            messages.success(
                request, 'The doctor profile has been updated successfully!')
            return redirect('core:view_doctor_profile', user_id=user_queryset.id)
    else:
        user_form = UserEditForm(instance=user_queryset)

    context = {
        'user': user_queryset,
        'user_form': user_form,
        'page_title': 'Doctor Management',
        'active_page': 'doctor',
    }

    return render(request, 'doctor/edit_doctor_profile.html', context)


@AllowedUsers(allowed_roles=['Administrator', 'Staff'])
@login_required(login_url='login')
def staff(request):
    staff_queryset = User.objects.filter(role='Staff').order_by('first_name')

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        staff_queryset = staff_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    # Add filter
    position_filter = request.GET.get('position', '')
    if position_filter:
        staff_queryset = staff_queryset.filter(
            position__iexact=position_filter)

    # Get unique positions for the filter dropdown
    positions = User.objects.filter(role='Staff').values_list(
        'position', flat=True).distinct()

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
        'position_filter': position_filter,
        'positions': positions,
    }

    return render(request, 'staff/staff.html', context)


@login_required(login_url='login')
@AllowedUsers(allowed_roles=['Administrator', 'Staff'])
def view_staff_profile(request, user_id):
    staff_queryset = User.objects.get(pk=user_id)

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
        'staff': staff_queryset,
    }

    return render(request, 'staff/view_staff_profile.html', context)


@login_required(login_url='login')
@AllowedUsers(allowed_roles=['Administrator'])
def edit_staff_profile(request, user_id):
    staff_queryset = User.objects.get(pk=user_id)

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
            request.POST, request.FILES, instance=staff_queryset)

        if user_form.is_valid():
            user_form.save()

            messages.success(
                request, 'The staff profile has been updated successfully!')
            return redirect('core:view_staff_profile', user_id=staff_queryset.id)
    else:
        user_form = UserEditForm(instance=staff_queryset)

    context = {
        'staff': staff_queryset,
        'user_form': user_form,
        'page_title': 'Staff Management',
        'active_page': 'staff',
    }

    return render(request, 'staff/edit_staff_profile.html', context)


@login_required(login_url='login')
def patient(request):
    patient_queryset = Patient.objects.all().order_by('-date_created')

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        patient_queryset = patient_queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Add filter
    blood_group_filter = request.GET.get('blood_group', '')
    if blood_group_filter:
        patient_queryset = patient_queryset.filter(
            blood_group__iexact=blood_group_filter)

    # Get unique blood_groups for the filter dropdown
    blood_groups = Patient.objects.all().values_list(
        'blood_group', flat=True).distinct()

    # Pagination
    paginator = Paginator(patient_queryset, 8)
    page = request.GET.get('page', 1)
    patient_list = paginator.get_page(page)

    # patient needs to be deleted
    if request.method == 'POST' and 'delete_patient_id' in request.POST:
        patient_id_to_delete = request.POST['delete_patient_id']
        patient_to_delete = Patient.objects.get(id=patient_id_to_delete)
        patient_to_delete.delete()
        messages.success(request, f"Patient {
                         patient_to_delete.name} has been deleted.")

    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
        'patients': patient_list,
        'total_patient': patient_queryset.count(),
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'blood_groups': blood_groups,
    }

    return render(request, 'patient/patient.html', context)


class PatientFormWizard(SessionWizardView):
    form_list = [PatientForm, MedicalHistoryForm,
                 DentalChartForm, TreatmentPlanForm]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "patient"))

    TEMPLATES = {
        "0": "patient/general.html",
        "1": "patient/history.html",
        '2': 'patient/dental_chart.html',
        '3': 'patient/treatment_plan.html',
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
        if self.steps.current == '2':  # Dental Chart step
            if self.request.method == 'POST' and self.steps.current == self.get_step_index():
                context['tooth_record_formset'] = ToothRecordFormSet(
                    self.request.POST)
            else:
                context['tooth_record_formset'] = ToothRecordFormSet()
        return context

    def get_form_instance(self, step):
        if step == '0':  # Patient Form
            return Patient()
        elif step == '1':  # Medical History Form
            return MedicalHistory()
        elif step == '2':  # Dental Chart Form
            return DentalChart()
        elif step == '3':  # Treatment Plan Form
            return TreatmentPlan()
        return None

    def post(self, *args, **kwargs):
        current_step = self.steps.current

        if current_step == '0':  # Save patient in step 0
            form = self.get_form(step=current_step, data=self.request.POST)
            if form.is_valid():
                patient = form.save()
                self.storage.extra_data['patient_id'] = patient.id
                self.storage.set_step_data(
                    current_step, self.process_step(form))
                return self.render_next_step(form)
            return self.render(form)

        if current_step == '2':  # Dental Chart step
            form = self.get_form(step=current_step, data=self.request.POST)
            tooth_record_formset = ToothRecordFormSet(self.request.POST)

            if form.is_valid() and tooth_record_formset.is_valid():
                self.storage.set_step_data(
                    current_step, self.process_step(form))
                dental_chart = form.save(commit=False)
                dental_chart.patient = self.get_patient_instance()
                dental_chart.save()

                tooth_record_formset.instance = dental_chart
                tooth_record_formset.save()

                return self.render_next_step(form)
            else:
                return self.render(form, tooth_record_formset=tooth_record_formset)

        return super().post(*args, **kwargs)

    def get_patient_instance(self):

        patient_id = self.storage.extra_data.get('patient_id')
        if patient_id:
            return Patient.objects.get(id=patient_id)
        patient_data = self.get_cleaned_data_for_step('0')
        if patient_data:
            patient = Patient(**patient_data)
            patient.save()
            self.storage.extra_data['patient_id'] = patient.id
            return patient
        return None

    def done(self, form_list, **kwargs):
        request = self.request

        patient = self.get_patient_instance()
        if not patient:
            patient = form_list[0].save()

        # Save medical history
        medical_history = form_list[1].save(commit=False)
        medical_history.patient = patient
        medical_history.save()

        dental_chart = DentalChart.objects.filter(patient=patient).first()

        # Save treatment plan
        treatment_plan = form_list[3].save(commit=False)
        treatment_plan.patient = patient
        treatment_plan.save()

        messages.success(request, 'The patient has been added successfully!')
        return redirect('core:patient')


@login_required(login_url='login')
def edit_patient_profile(request, patient_id, step=0):
    patient = get_object_or_404(Patient, id=patient_id)
    step = str(step)

    TEMPLATES = {
        "0": "patient/general.html",
        "1": "patient/history.html",
        "2": "patient/dental_chart.html",
        "3": "patient/treatment_plan.html",
    }
    FORMS = {
        "0": PatientForm,
        "1": MedicalHistoryForm,
        "2": DentalChartForm,
        "3": TreatmentPlanForm,
    }

    if step == "0":
        instance = patient
    elif step == "1":
        instance, _ = MedicalHistory.objects.get_or_create(patient=patient)
    elif step == "2":
        instance, _ = DentalChart.objects.get_or_create(patient=patient)
    elif step == "3":
        instance, _ = TreatmentPlan.objects.get_or_create(patient=patient)
    else:
        return redirect('core:view_patient_profile', patient_id=patient_id)

    form_class = FORMS.get(step)
    tooth_record_formset = None
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if step == "2":
            tooth_record_formset = ToothRecordFormSet(
                request.POST, instance=instance)
            if form.is_valid() and tooth_record_formset.is_valid():
                saved_instance = form.save()
                tooth_record_formset.instance = saved_instance
                tooth_record_formset.save()
                messages.success(
                    request, "The patient details have been updated successfully!")
                return redirect('core:view_patient_profile', patient_id=patient_id)
        elif form.is_valid():
            form.save()
            messages.success(
                request, "The patient details have been updated successfully!")
            return redirect('core:view_patient_profile', patient_id=patient_id)
    else:
        form = form_class(instance=instance)
        if step == "2":
            tooth_record_formset = ToothRecordFormSet(instance=instance)

    wizard = {
        'form': form,
        'management_form': '',
        'steps': {
            'current': step,
        }
    }

    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
        'is_editing': True,
        'patient_id': patient_id,
        'wizard': wizard,
    }
    if step == "2" and tooth_record_formset:
        context['tooth_record_formset'] = tooth_record_formset

    template = TEMPLATES.get(step, "patient/general.html")
    return render(request, template, context)


class EditPatientFormWizard(SessionWizardView):
    form_list = [PatientForm, MedicalHistoryForm,
                 DentalChartForm, TreatmentPlanForm]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "patient"))

    TEMPLATES = {
        "0": "patient/general.html",
        "1": "patient/history.html",
        '2': 'patient/dental_chart.html',
        '3': 'patient/treatment_plan.html',
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
        if self.steps.current == '2':  # Dental Chart step
            dental_chart = self.get_form_instance('2')
            if self.request.method == 'POST' and self.steps.current == self.get_step_index():
                context['tooth_record_formset'] = ToothRecordFormSet(
                    self.request.POST, instance=dental_chart)
            else:
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
        elif step == '2':  # Dental Chart Form
            dental_chart, created = DentalChart.objects.get_or_create(
                patient=patient)
            return dental_chart
        elif step == '3':  # Treatment Plan Form
            treatment_plan, created = TreatmentPlan.objects.get_or_create(
                patient=patient)
            return treatment_plan
        return None

    def post(self, *args, **kwargs):
        current_step = self.steps.current

        if current_step == '0':  # Patient info step
            form = self.get_form(step=current_step, data=self.request.POST)
            if form.is_valid():
                form.save()  # Update patient directly
                self.storage.set_step_data(
                    current_step, self.process_step(form))
                return self.render_next_step(form)
            return self.render(form)

        if current_step == '2':  # Dental Chart step
            form = self.get_form(step=current_step, data=self.request.POST)
            dental_chart = self.get_form_instance('2')
            tooth_record_formset = ToothRecordFormSet(
                self.request.POST, instance=dental_chart)

            if form.is_valid() and tooth_record_formset.is_valid():
                self.storage.set_step_data(
                    current_step, self.process_step(form))
                form.save()  # Update dental chart
                tooth_record_formset.save()  # Save tooth records
                return self.render_next_step(form)
            else:
                return self.render(form, tooth_record_formset=tooth_record_formset)

        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        request = self.request
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)

        # Medical history
        medical_history_form = form_list[1]
        medical_history, created = MedicalHistory.objects.update_or_create(
            patient=patient, defaults=medical_history_form.cleaned_data
        )

        dental_chart = DentalChart.objects.filter(patient=patient).first()

        # Treatment plan
        treatment_plan_form = form_list[3]
        treatment_plan, created = TreatmentPlan.objects.update_or_create(
            patient=patient, defaults=treatment_plan_form.cleaned_data
        )

        messages.success(
            request, 'The patient details have been updated successfully!')
        return redirect('core:patient')


def get_patient_data(patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    patient_history = getattr(patient, 'patient_history', None)
    dental_chart = getattr(patient, 'dental_chart', None)
    treatment_plan = getattr(patient, 'treatment_plan', None)
    completed_appointments = Appointment.objects.filter(
        patient=patient, status='Completed'
    ).prefetch_related('treatment_records')

    treatment_history = [
        {
            'appointment_id': appointment.id,
            'appointment_date': appointment.date,
            'treatment_record': appointment.treatment_records.first()
        }
        for appointment in completed_appointments
        if appointment.treatment_records.exists()
    ]

    medical_history_sections = {
        "General": ["marked_weight_change"],
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
        "Extraction": ["prev_extraction", "date_of_last_extraction", "untoward_reaction", "untoward_reaction_specifics", "local_anesthesia_use"],
        "Hospitalization": ["hospitalized", "admission_date", "hospitalization_specifics"],
        "Allergies": ["sleeping_pills", "aspirin", "food", "penicilin", "antibiotics", "sulfa_drugs", "local_anesthesia", "others", "specifics"],
        "Habits": ["smoking", "tobacco_chewing", "alcohol", "betel_nuts", "paan_chewing"],
        "Oral_Hygiene": ["stain", "calculus", "halitosis"]
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

    return {
        'patient': patient,
        'patient_history': patient_history,
        'dental_chart': dental_chart,
        'treatment_plan': treatment_plan,
        'treatment_history': treatment_history,
        'medical_history_data': medical_history_data,
        'tooth_records': dental_chart.tooth_records.all() if dental_chart else None
    }


@login_required(login_url='login')
def view_patient_profile(request, patient_id):
    data = get_patient_data(patient_id)

    # Handle patient deletion
    if request.method == 'POST' and 'delete_patient_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            patient_id_to_delete = request.POST['delete_patient_id']
            patient_to_delete = Patient.objects.get(id=patient_id_to_delete)
            patient_to_delete.delete()
            messages.success(
                request, f"Patient {patient_to_delete.name} has been deleted.")
            return redirect('core:patient')

    context = {
        'page_title': 'Patient Management',
        'active_page': 'patient',
        **data
    }

    return render(request, 'patient/view_patient_profile.html', context)


def generate_patient_pdf(request, patient_id):
    data = get_patient_data(patient_id)
    patient = data['patient']
    patient_history = data['patient_history']
    dental_chart = data['dental_chart']
    treatment_plan = data['treatment_plan']
    treatment_history = data['treatment_history']
    medical_history_data = data['medical_history_data']
    tooth_records = data['tooth_records']

    # Create a PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        spaceAfter=10,
        fontSize=14,
    )
    sub_section_style = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        textColor=colors.HexColor('#000000'),
        spaceAfter=8,
        fontSize=14,
    )
    normal_colored_style = ParagraphStyle(
        'NormalColored',
        parent=styles['Normal'],
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        fontSize=11,
    )

    elements = []

    logo_path = None
    logo_relative_path = 'images/logo/logo2.png'

    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        logo_path = os.path.join(settings.STATIC_ROOT, logo_relative_path)

    if not logo_path or not os.path.exists(logo_path):
        for static_dir in settings.STATICFILES_DIRS:
            potential_path = os.path.join(static_dir, logo_relative_path)
            if os.path.exists(potential_path):
                logo_path = potential_path
                break

    clinic_details = {
        'name': 'Smile by Dr. Kareen',
        'address': 'Pulchowk-3, Damkal Chowk, Lalitpur, Nepal',
        'address2': '(Opposite to Sumeru Hospital)',
        'tel': '1 5920775',
        'contact': '+977 9851359775',
        'email': 'smilebydrkareen@gmail.com'
    }

    header_data = [
        [
            Image(logo_path, width=150, height=100) if logo_path and os.path.exists(
                logo_path) else Paragraph("Logo not found", styles['Normal']),
            [
                Paragraph(f"{clinic_details['name']}", styles['Heading1']),
                Paragraph(
                    f"{clinic_details['address']}<br/>{clinic_details['address2']}<br/>Tel: {clinic_details['tel']}<br/>Contact: {clinic_details['contact']}<br/>Email: {clinic_details['email']}", styles['Normal'])
            ]
        ]
    ]
    header_table = Table(header_data, colWidths=[3*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0, colors.white)
    ]))

    elements.append(header_table)

    # Solid line after header
    elements.append(Spacer(1, 6))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 18))

    # Patient Name (Highlighted)
    elements.append(
        Paragraph(f"Patient Name: {patient.name}", style=styles['Heading1']))
    elements.append(Spacer(1, 6))

    # Patient Information (Grid)
    elements.append(Paragraph("<u>Patient Information</u>", section_style))
    patient_data = [
        ["ID:", str(patient.id), "Contact:", patient.contact],
        ["Address:", patient.address or "N/A", "Gender:", patient.gender],
        ["Blood Group:", patient.blood_group, "Age:",
            str(patient.age) if patient.age else "N/A"],
        ["Email:", patient.email or "N/A", "Telephone:", patient.telephone or "N/A"],
        ["Occupation:", patient.occupation or "N/A",
            "Nationality:", patient.nationality or "N/A"],
        ["Marital Status:", patient.marital_status,
            "Referred By:", patient.reffered_by or "N/A"],
        ["Date Added:", patient.date_created.strftime(
            '%Y-%m-%d') if patient.date_created else "N/A", "", ""]
    ]
    patient_grid = Table(patient_data, colWidths=[
                         1.25*inch, 2*inch, 1.25*inch, 2*inch])
    patient_grid.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(patient_grid)

    elements.append(Spacer(1, 12))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 12))

    # Emergency Contact
    elements.append(Paragraph("<u>Emergency Contact</u>", section_style))
    elements.append(
        Paragraph(f"Name: {patient.emergency_contact_name}", normal_colored_style))
    elements.append(Paragraph(
        f"Contact: {patient.emergency_contact_contact}", normal_colored_style))
    elements.append(Paragraph(
        f"Address: {patient.emergency_contact_address or 'N/A'}", normal_colored_style))
    elements.append(Paragraph(
        f"Relation: {patient.emergency_contact_relation or 'N/A'}", normal_colored_style))

    elements.append(Spacer(1, 12))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))

    # Medical History
    elements.append(FrameBreak())
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<u>Medical History</u>", section_style))
    for section, data in medical_history_data.items():
        elements.append(Paragraph(section, sub_section_style))
        for key, value in data.items():
            elements.append(
                Paragraph(f"{key.replace('_', ' ').title()}: {value}", normal_colored_style))
        elements.append(Spacer(1, 6))
    elements.append(Spacer(1, 6))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 12))

    # Dental Chart
    elements.append(Paragraph("<u>Dental Chart</u>", section_style))
    if tooth_records:
        tooth_data = [["Tooth No", "Condition", "Description"]] + [
            [record.tooth_no, record.condition or "N/A", record.description or "N/A"]
            for record in tooth_records
        ]
        tooth_table = Table(tooth_data, colWidths=[2*inch, 2*inch, 2*inch])
        tooth_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c7c7c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 13),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#7c7c7c'))
        ]))
        elements.append(tooth_table)
    else:
        elements.append(
            Paragraph("No dental records available", normal_colored_style))

    elements.append(Spacer(1, 12))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))

    # Treatment Plan
    elements.append(FrameBreak())
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<u>Treatment Plan</u>", section_style))
    elements.append(Paragraph(
        treatment_plan.treatment_plan if treatment_plan and treatment_plan.treatment_plan else "No treatment plan specified",
        normal_colored_style
    ))

    elements.append(Spacer(1, 12))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))
    elements.append(Spacer(1, 12))

    # Treatment History
    elements.append(Paragraph("<u>Treatment History</u>", section_style))
    if treatment_history:
        treatment_data = [["Appt. ID", "Date", "Treatment Type", "T.Cost"]] + [
            [
                treatment['appointment_id'],
                treatment['appointment_date'].strftime('%Y-%m-%d'),
                treatment['treatment_record'].treatment_type or "N/A",
                str(treatment['treatment_record'].treatment_cost or 0)
            ]
            for treatment in treatment_history
        ]
        treatment_table = Table(treatment_data, colWidths=[
                                1.5*inch, 1.5*inch, 2*inch, 1*inch])
        treatment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c7c7c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 13),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#7c7c7c'))
        ]))
        elements.append(treatment_table)
    else:
        elements.append(
            Paragraph("No treatment history available", normal_colored_style))

    elements.append(Spacer(1, 12))
    elements.append(Table([['']], colWidths=[6.5*inch], rowHeights=[0.05*inch],
                    style=TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000'))])))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"{patient.name}_Report_{timezone.now().date()}.pdf")


@login_required(login_url='login')
def appointment(request):
    appointment_queryset = Appointment.objects.all().order_by('-date', '-time')

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
            Q(patient__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Add filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointment_queryset = appointment_queryset.filter(
            status__iexact=status_filter)
    status = Appointment.objects.all().values_list(
        'status', flat=True).distinct()

    # Date range filter
    date_range = request.GET.get('date_range', '')
    if date_range:
        try:
            dates = date_range.split(' to ')
            if len(dates) == 1:  # Single date selected
                selected_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                appointment_queryset = appointment_queryset.filter(
                    date=selected_date)
            elif len(dates) == 2:  # Date range selected
                start_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    dates[1].strip(), '%Y-%m-%d').date()
                appointment_queryset = appointment_queryset.filter(
                    date__range=[start_date, end_date]
                )
        except (ValueError, AttributeError):
            pass

    # Pagination
    paginator = Paginator(appointment_queryset, 8)
    page = request.GET.get('page', 1)
    appointment_list = paginator.get_page(page)

    appointments_data = [
        {
            'id': app.id,
            'title': f"Appointment - {app.patient.name}",
            'start': f"{app.date.isoformat()}T{app.time}",
            'extendedProps': {
                'patient_name': app.patient.name,
                'description': app.description or 'No description provided',
                'status': app.status,
                'appointment_id': app.id,
            }
        }
        for app in appointment_queryset
    ]

    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
        'appointments': appointment_list,
        'total_appointment': appointment_queryset.count(),
        'search_query': search_query,
        'status_filter': status_filter,
        'status': status,
        'appointments_schedule': appointments_data,
        'date_range': date_range,
    }

    return render(request, 'appointment/appointment.html', context)


class AppointmentFormWizard(SessionWizardView):
    form_list = [AppointmentForm, TreatmentRecordForm,
                 TreatmentDoctorFormSet, PurchasedProductFormSet]

    TEMPLATES = {
        '0': 'appointment/add_appointment.html',
        '1': 'appointment/add_treatment.html',
        '2': 'appointment/add_treatment_doctor.html',
        '3': 'appointment/add_purchased_product.html',
        # '4': 'appointment/add_payment.html',
    }

    def get_template_names(self):
        return [self.TEMPLATES.get(str(self.steps.current), "appointment/add_appointment.html")]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context.update({
            'page_title': 'Appointment Management',
            'active_page': 'appointment',
            'patients': Patient.objects.all(),
            'doctors': User.objects.filter(role='Doctor')

        })
        if self.steps.current == '2':
            if self.storage.get_step_data('2'):
                treatment_doctor_formset = TreatmentDoctorFormSet(
                    self.storage.get_step_data('2'),
                    prefix='treatment_doctors'
                )
            else:
                treatment_doctor_formset = TreatmentDoctorFormSet(
                    prefix='treatment_doctors',
                    instance=TreatmentRecord()
                )
            context['treatment_doctor_formset'] = treatment_doctor_formset
        if self.steps.current == '3':
            if self.storage.get_step_data('3'):
                purchased_product_formset = PurchasedProductFormSet(
                    self.storage.get_step_data('3'),
                    prefix='purchased_products'
                )
            else:
                purchased_product_formset = PurchasedProductFormSet(
                    prefix='purchased_products',
                    instance=Appointment()
                )
            context['purchased_product_formset'] = purchased_product_formset
        return context

    def get_form_instance(self, step):
        if step == '0':
            return Appointment()
        elif step == '1':
            return TreatmentRecord()
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

        treatment_doctor_data = self.storage.get_step_data('2')
        if treatment_doctor_data:
            treatment_doctor_formset = TreatmentDoctorFormSet(
                treatment_doctor_data,
                instance=treatment,
                prefix='treatment_doctors'
            )
            if treatment_doctor_formset.is_valid():
                treatment_doctor_formset.save()

        purchased_product_data = self.storage.get_step_data('3')
        if purchased_product_data:
            purchased_product_formset = PurchasedProductFormSet(
                purchased_product_data,
                instance=appointment,
                prefix='purchased_products'
            )
            if purchased_product_formset.is_valid():
                purchased_product_formset.save()

        payment, created = Payment.objects.get_or_create(
            appointment=appointment)
        payment.save()

        messages.success(
            request, 'The appointment has been added successfully!')
        return redirect('core:appointment')


@login_required(login_url='login')
def edit_appointment(request, appointment_id, step=0):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    step = str(step)

    TEMPLATES = {
        "0": "appointment/add_appointment.html",
        "1": "appointment/add_treatment.html",
        "2": "appointment/add_treatment_doctor.html",
        "3": "appointment/add_purchased_product.html",
        "4": "appointment/add_payment.html",
    }
    FORMS = {
        "0": AppointmentForm,
        "1": TreatmentRecordForm,
        "2": TreatmentDoctorFormSet,
        "3": PurchasedProductFormSet,
        "4": PaymentForm,
    }

    if step == "0":
        instance = appointment
    elif step == "1":
        instance, _ = TreatmentRecord.objects.get_or_create(
            appointment=appointment)
    elif step == "2":
        instance, _ = TreatmentRecord.objects.get_or_create(
            appointment=appointment)
    elif step == "3":
        instance = appointment
    elif step == "4":
        instance, _ = Payment.objects.get_or_create(appointment=appointment)
    else:
        return redirect('core:view_appointment', appointment_id=appointment_id)

    form_class = FORMS.get(step)
    treatment_doctor_formset = None
    purchased_product_formset = None

    if request.method == "POST":
        if step == "2":
            treatment_doctor_formset = TreatmentDoctorFormSet(
                request.POST, instance=instance, prefix='treatment_doctors')
            if treatment_doctor_formset.is_valid():
                treatment_doctor_formset.save()
                payment, _ = Payment.objects.get_or_create(
                    appointment=appointment)
                payment.save()
                messages.success(
                    request, "The treatment doctors have been updated successfully!")
                return redirect('core:view_appointment', appointment_id=appointment_id)
        elif step == "3":
            purchased_product_formset = PurchasedProductFormSet(
                request.POST, instance=instance, prefix='purchased_products')
            if purchased_product_formset.is_valid():
                purchased_product_formset.save()
                payment, _ = Payment.objects.get_or_create(
                    appointment=appointment)
                payment.save()
                messages.success(
                    request, "The purchased products have been updated successfully!")
                return redirect('core:view_appointment', appointment_id=appointment_id)
        else:
            form = form_class(request.POST, instance=instance)
            if form.is_valid():
                saved_instance = form.save()
                payment, _ = Payment.objects.get_or_create(
                    appointment=appointment)
                payment.save()
                messages.success(
                    request, "The appointment details have been updated successfully!")
                return redirect('core:view_appointment', appointment_id=appointment_id)
            else:
                print(f"Form errors for step {step}: {form.errors}")

    else:
        if step == "2":
            treatment_doctor_formset = TreatmentDoctorFormSet(
                instance=instance, prefix='treatment_doctors')
            form = None
        elif step == "3":
            purchased_product_formset = PurchasedProductFormSet(
                instance=instance, prefix='purchased_products')
            form = None
        else:
            form = form_class(instance=instance)

    wizard = {
        'form': form if 'form' in locals() else None,
        'management_form': '',
        'steps': {'current': step}
    }

    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
        'is_editing': True,
        'appointment_id': appointment_id,
        'wizard': wizard,
        'doctors': User.objects.filter(role='Doctor'),
    }
    if step == "2" and treatment_doctor_formset:
        context['treatment_doctor_formset'] = treatment_doctor_formset
    elif step == "3" and purchased_product_formset:
        context['purchased_product_formset'] = purchased_product_formset
    elif step == "4":
        payment = instance
        treatment_cost = sum(
            tr.treatment_cost or 0 for tr in appointment.treatment_records.all())
        lab_cost = sum(
            tr.lab_cost or 0 for tr in appointment.treatment_records.all() if tr.lab)
        x_ray_cost = sum(
            tr.x_ray_cost or 0 for tr in appointment.treatment_records.all() if tr.x_ray)
        products_total = sum(
            pp.total_amt or 0 for pp in appointment.purchased_products.all())
        context.update({
            'treatment_cost': treatment_cost,
            'lab_cost': lab_cost,
            'x_ray_cost': x_ray_cost,
            'products_total': products_total,
        })

    template = TEMPLATES.get(step, "appointment/add_appointment.html")
    return render(request, template, context)


# class EditAppointmentWizard(SessionWizardView):
#     form_list = [AppointmentForm, TreatmentRecordForm,
#                  TreatmentDoctorFormSet, PurchasedProductFormSet, PaymentForm]
#     file_storage = FileSystemStorage(
#         location=os.path.join("media", "appointment"))
#     TEMPLATES = {
#         '0': 'appointment/add_appointment.html',
#         '1': 'appointment/add_treatment.html',
#         '2': 'appointment/add_treatment_doctor.html',
#         '3': 'appointment/add_purchased_product.html',
#         '4': 'appointment/add_payment.html',
#     }

#     def get_template_names(self):
#         return [self.TEMPLATES.get(str(self.steps.current), "appointment/add_appointment.html")]

#     def get_context_data(self, form, **kwargs):
#         context = super().get_context_data(form=form, **kwargs)
#         appointment_id = self.kwargs.get('appointment_id')
#         appointment = get_object_or_404(Appointment, id=appointment_id)

#         context.update({
#             'page_title': 'Appointment Management',
#             'active_page': 'appointment',
#             'is_editing': True,
#             'appointment_id': appointment_id,
#             'doctors': User.objects.filter(role='Doctor'),
#             'patients': Patient.objects.all(),
#         })

#         if self.steps.current == '2':
#             # For TreatmentDoctorFormSet
#             treatment = None
#             if appointment_id:
#                 appointment = get_object_or_404(Appointment, id=appointment_id)
#                 treatment = TreatmentRecord.objects.filter(
#                     appointment=appointment).first()

#             context['treatment_doctor_formset'] = form
#             if isinstance(form, TreatmentDoctorFormSet):
#                 if self.storage.get_step_data('2'):
#                     form.initial = self.storage.get_step_data('2')
#                 context['treatment_doctor_formset'] = form

#         elif self.steps.current == '3':
#             # For PurchasedProductFormSet
#             if appointment_id:
#                 appointment = get_object_or_404(Appointment, id=appointment_id)
#                 context['purchased_product_formset'] = form
#                 if isinstance(form, PurchasedProductFormSet):
#                     if self.storage.get_step_data('3'):
#                         form.initial = self.storage.get_step_data('3')
#                     context['purchased_product_formset'] = form

#         return context

#     def get_form(self, step=None, data=None, files=None):
#         form = super().get_form(step, data, files)

#         appointment_id = self.kwargs.get('appointment_id')
#         if appointment_id:
#             appointment = get_object_or_404(Appointment, id=appointment_id)

#             if step == '2':
#                 treatment = TreatmentRecord.objects.filter(
#                     appointment=appointment).first()
#                 if isinstance(form, TreatmentDoctorFormSet):
#                     if treatment:
#                         form.instance = treatment
#             elif step == '3':
#                 if isinstance(form, PurchasedProductFormSet):
#                     form.instance = appointment

#         return form

#     def get_form_instance(self, step):
#         appointment_id = self.kwargs.get('appointment_id')
#         if not appointment_id:
#             return None

#         appointment = get_object_or_404(Appointment, id=appointment_id)

#         if step == '0':
#             return appointment
#         elif step == '1':
#             treatment = TreatmentRecord.objects.filter(
#                 appointment=appointment).first()
#             if not treatment:
#                 treatment = TreatmentRecord(appointment=appointment)
#             return treatment
#         elif step == '2':
#             treatment = TreatmentRecord.objects.filter(
#                 appointment=appointment).first()
#             if not treatment:
#                 treatment = TreatmentRecord(appointment=appointment)
#                 treatment.save()
#             return treatment
#         elif step == '3':
#             return appointment
#         return None

#     def done(self, form_list, **kwargs):
#         request = self.request
#         appointment_id = self.kwargs.get('appointment_id')
#         appointment = get_object_or_404(Appointment, id=appointment_id)

#         # Save Appointment data
#         appointment_form = form_list[0]
#         for field, value in appointment_form.cleaned_data.items():
#             setattr(appointment, field, value)
#         appointment.save()

#         # Save Treatment data
#         treatment_form = form_list[1]
#         treatment = TreatmentRecord.objects.filter(
#             appointment=appointment).first()
#         if not treatment:
#             treatment = TreatmentRecord(appointment=appointment)

#         for field, value in treatment_form.cleaned_data.items():
#             setattr(treatment, field, value)
#         treatment.save()

#         # Save multiple TreatmentDoctor records
#         treatment_doctor_formset = form_list[2]
#         if treatment_doctor_formset.is_valid():
#             treatment_doctor_formset.instance = treatment
#             treatment_doctor_formset.save()

#         # Save multiple PurchasedProduct records
#         purchased_product_formset = form_list[3]
#         if purchased_product_formset.is_valid():
#             purchased_product_formset.instance = appointment
#             purchased_product_formset.save()

#         messages.success(
#             request, 'The appointment has been updated successfully!')
#         return redirect('core:appointment')


class EditAppointmentWizard(SessionWizardView):
    form_list = [AppointmentForm, TreatmentRecordForm,
                 TreatmentDoctorFormSet, PurchasedProductFormSet, PaymentForm]
    file_storage = FileSystemStorage(
        location=os.path.join("media", "appointment"))
    TEMPLATES = {str(i): f'appointment/add_{name}.html' for i, name in enumerate([
        'appointment', 'treatment', 'treatment_doctor', 'purchased_product', 'payment'
    ])}

    def get_template_names(self):
        return [self.TEMPLATES.get(self.steps.current, "appointment/add_appointment.html")]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        context.update({
            'page_title': 'Appointment Management',
            'active_page': 'appointment',
            'is_editing': True,
            'appointment_id': appointment_id,
            'doctors': User.objects.filter(role='Doctor'),
            'patients': Patient.objects.all(),
        })

        step = self.steps.current
        if step == '2':
            context['treatment_doctor_formset'] = form
        elif step == '3':
            context['purchased_product_formset'] = form
        elif step == '4':
            treatment_data = self.storage.get_step_data('1') or {}
            product_data = self.storage.get_step_data('3') or {}
            payment_data = self.storage.get_step_data('4') or {}

            # Treatment costs from Step 1
            treatment_cost = Decimal(
                treatment_data.get('treatment_cost', '0') or '0')
            x_ray_cost = Decimal(treatment_data.get(
                'x_ray_cost', '0') or '0')
            lab_cost = Decimal(treatment_data.get(
                'lab_cost', '0') or '0')

            product_cost = Decimal('0')
            if product_data:
                total_forms = int(product_data.get(
                    'purchased_products-TOTAL_FORMS', 0))
                for i in range(total_forms):
                    # Skip deleted products
                    if f'purchased_products-{i}-DELETE' not in product_data:
                        rate = Decimal(product_data.get(
                            f'purchased_products-{i}-rate', '0') or '0')
                        quantity = Decimal(product_data.get(
                            f'purchased_products-{i}-quantity', '0') or '0')
                        product_cost += rate * quantity

            additional_cost = Decimal(
                payment_data.get('additional_cost', '0') or '0')
            discount_amount = Decimal(
                payment_data.get('discount_amount', '0') or '0')
            paid_amount = Decimal(payment_data.get('paid_amount', '0') or '0')

            final_amount = (treatment_cost + x_ray_cost + lab_cost +
                            product_cost + additional_cost) - discount_amount
            remaining_balance = final_amount - paid_amount

            context.update({
                'payment': None,
                'treatment_cost': treatment_cost,
                'x_ray_cost': x_ray_cost,
                'lab_cost': lab_cost,
                'products_total': product_cost,
                'additional_cost': additional_cost,
                'discount_amount': discount_amount,
                'final_amount': final_amount,
                'remaining_balance': remaining_balance,
                'paid_amount': paid_amount,
            })

        return context

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        appointment_id = self.kwargs.get('appointment_id')
        if not appointment_id:
            return super().get_form(step=step, data=data, files=files)

        appointment = get_object_or_404(Appointment, id=appointment_id)
        instances = {
            '0': appointment,
            '1': TreatmentRecord.objects.filter(appointment=appointment).first() or TreatmentRecord(appointment=appointment),
            '2': TreatmentRecord.objects.filter(appointment=appointment).first() or TreatmentRecord(appointment=appointment),
            '3': appointment,
            '4': Payment.objects.filter(appointment=appointment).first() or Payment(appointment=appointment),
        }
        form_classes = {
            '0': AppointmentForm,
            '1': TreatmentRecordForm,
            '2': lambda *args, **kwargs: TreatmentDoctorFormSet(*args, prefix='treatment_doctors', **kwargs),
            '3': lambda *args, **kwargs: PurchasedProductFormSet(*args, prefix='purchased_products', **kwargs),
            '4': PaymentForm,
        }

        instance = instances.get(step)
        form_class = form_classes.get(step)
        if not instance or not form_class:
            return super().get_form(step=step, data=data, files=files)

        if data is None and not self.request.POST:
            data = self.storage.get_step_data(step)

        return form_class(data=data, files=files, instance=instance)

    def process_step(self, form):
        if form.is_valid():
            return self.get_form_step_data(form)
        else:
            print(f"Form errors at step {self.steps.current}: {form.errors}")
            return self.get_form_step_data(form)

    def done(self, form_list, **kwargs):
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        appointment_form = form_list[0]
        if appointment_form.is_valid():
            for field, value in appointment_form.cleaned_data.items():
                setattr(appointment, field, value)
            appointment.save()

        treatment_form = form_list[1]
        if treatment_form.is_valid():
            treatment = TreatmentRecord.objects.filter(
                appointment=appointment).first() or TreatmentRecord(appointment=appointment)
            for field, value in treatment_form.cleaned_data.items():
                setattr(treatment, field, value)
            treatment.save()

        treatment_doctor_formset = form_list[2]
        if treatment_doctor_formset.is_valid():
            treatment = TreatmentRecord.objects.filter(
                appointment=appointment).first()
            if treatment:
                treatment_doctor_formset.instance = treatment
                treatment_doctor_formset.save()

        purchased_product_formset = form_list[3]
        if purchased_product_formset.is_valid():
            purchased_product_formset.instance = appointment
            purchased_product_formset.save()

        payment_form = form_list[4]
        if payment_form.is_valid():
            payment = Payment.objects.filter(
                appointment=appointment).first() or Payment(appointment=appointment)
            for field, value in payment_form.cleaned_data.items():
                setattr(payment, field, value)
            payment.save()

        messages.success(
            self.request, 'The appointment has been updated successfully!')
        return redirect('core:view_appointment', appointment_id=appointment_id)


@login_required(login_url='login')
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    treatment_plan = appointment.patient.treatment_plan if hasattr(
        appointment.patient, 'treatment_plan') else None
    treatment_records = TreatmentRecord.objects.filter(
        appointment=appointment).first()
    treatment_doctors = TreatmentDoctor.objects.filter(
        treatment_record__appointment=appointment)
    purchased_products = PurchasedProduct.objects.filter(
        appointment=appointment)
    payment = Payment.objects.filter(appointment=appointment).first()

    treatment_cost = sum(
        tr.treatment_cost or 0 for tr in appointment.treatment_records.all())
    lab_cost = sum(
        tr.lab_cost or 0 for tr in appointment.treatment_records.all() if tr.lab)
    x_ray_cost = sum(
        tr.x_ray_cost or 0 for tr in appointment.treatment_records.all() if tr.x_ray)
    products_total = sum(
        pp.total_amt or 0 for pp in appointment.purchased_products.all())
    # Handle deletion
    if request.method == 'POST' and 'delete_appointment_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            appointment_id_to_delete = request.POST['delete_appointment_id']
            appointment_to_delete = Appointment.objects.get(
                id=appointment_id_to_delete)
            appointment_to_delete.delete()
            messages.success(request, f"Appointment has been deleted.")
            return redirect('core:appointment')

    context = {
        'page_title': 'Appointment Management',
        'active_page': 'appointment',
        'appointment': appointment,
        'treatment_plan': treatment_plan,
        'treatment_records': treatment_records,
        'treatment_doctors': treatment_doctors,
        'lab_cost': lab_cost,
        'x_ray_cost': x_ray_cost,
        'treatment_cost': treatment_cost,
        'total_cost': lab_cost + x_ray_cost + treatment_cost,
        'purchased_products': purchased_products,
        'products_total': products_total,
        'payment': payment,
    }

    return render(request, 'appointment/view_appointment.html', context)


# @login_required(login_url='login')
# def schedule(request):
#     appointments = Appointment.objects.all()
#     appointments_data = [
#         {
#             'title': f"Appointment - {app.patient.name}",
#             'start': f"{app.date.isoformat()}T{app.time}",
#             'extendedProps': {
#                 'patient_name': app.patient.name,
#                 'description': app.description or 'No description provided',
#                 'status': app.status,
#             }
#         }
#         for app in appointments
#     ]

#     context = {
#         'page_title': 'Schedule Management',
#         'active_page': 'schedule',
#         'appointments': appointments_data,
#     }
#     return render(request, 'schedule/schedule.html', context)


@login_required(login_url='login')
@AdminOnly
def view_transaction(request):
    transaction_queryset = Transaction.objects.all().order_by('-date', '-time')

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transaction_queryset = transaction_queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # date range
    date_range = request.GET.get('date_range', '')
    if date_range:
        try:
            dates = date_range.split(' to ')
            if len(dates) == 1:  # Single date selected
                selected_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                transaction_queryset = transaction_queryset.filter(
                    date=selected_date)
            elif len(dates) == 2:  # Date range selected
                start_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    dates[1].strip(), '%Y-%m-%d').date()
                transaction_queryset = transaction_queryset.filter(
                    date__range=[start_date, end_date]
                )
        except (ValueError, AttributeError):
            pass

    # transaction needs to be deleted
    if request.method == 'POST' and 'delete_transaction_id' in request.POST:
        transaction_id_to_delete = request.POST['delete_transaction_id']
        transaction_to_delete = Transaction.objects.get(
            id=transaction_id_to_delete)
        transaction_to_delete.delete()
        messages.success(
            request, f"Transaction {transaction_to_delete.title}  has been deleted.")

    income_queryset = transaction_queryset.filter(type="Income")
    expense_queryset = transaction_queryset.filter(type="Expense")

    # Pagination
    income_paginator = Paginator(income_queryset, 8)
    income_page = request.GET.get('income_page', 1)
    income_transaction_list = income_paginator.get_page(income_page)

    expense_paginator = Paginator(expense_queryset, 8)
    expense_page = request.GET.get('expense_page', 1)
    expense_transaction_list = expense_paginator.get_page(expense_page)

    context = {
        'page_title': 'Transaction Management',
        'active_page': 'transaction',
        'income_transaction': income_transaction_list,
        'expense_transaction': expense_transaction_list,
        'total_transactions': transaction_queryset.count(),
        'income_transactions': income_queryset,
        'expense_transactions': expense_queryset,
        'total_income': sum([income.amount for income in income_queryset]),
        'total_expense': sum([expense.amount for expense in expense_queryset]),
        'net_profit': sum([income.amount for income in income_queryset]) - sum([expense.amount for expense in expense_queryset]),
        'search_query': search_query,
        'date_range': date_range,
    }
    return render(request, 'transaction/view_transaction.html', context)


@login_required(login_url='login')
@AdminOnly
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('core:view_transaction')
    else:
        form = TransactionForm()

    context = {
        'page_title': 'Transaction Management',
        'active_page': 'transaction',
        'form': form,
    }
    return render(request, 'transaction/add_transaction.html', context)


@login_required(login_url='login')
@AdminOnly
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(
        Transaction, id=transaction_id, user=request.user
    )

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('core:view_transaction')
    else:
        form = TransactionForm(instance=transaction)

    context = {
        'page_title': 'Edit Transaction',
        'active_page': 'transaction',
        'is_editing': True,
        'form': form,
        'transaction': transaction,
    }
    return render(request, 'transaction/add_transaction.html', context)


@login_required(login_url='login')
@AdminOnly
def statistics(request):
    time_filter = request.GET.get('filter', 'monthly')
    today = timezone.now().date()
    date_range = request.GET.get('date_range', '').strip()
    apply_date_filter = True
    start_date = None
    end_date = today

    # Initialize querysets
    transactions = Transaction.objects.all()
    treatments = TreatmentRecord.objects.all()
    payments = Payment.objects.all()
    purchased_products = PurchasedProduct.objects.all()
    patients = Patient.objects.all()
    users = User.objects.all()
    products = PurchasedProduct.objects.all()

    # Determine date range
    if date_range:
        try:
            dates = date_range.split(' to ')
            if len(dates) == 1 and dates[0]:
                start_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                end_date = start_date
            elif len(dates) == 2:
                start_date = datetime.strptime(
                    dates[0].strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    dates[1].strip(), '%Y-%m-%d').date()
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
        except (ValueError, AttributeError) as e:
            start_date = today - timedelta(days=90)
    elif time_filter == 'overall':
        apply_date_filter = False
    elif time_filter == 'daily':
        start_date = today
    elif time_filter == 'weekly':
        days_since_sunday = (today.weekday() + 1) % 7
        start_date = today - timedelta(days=days_since_sunday)
    elif time_filter == 'monthly':
        start_date = today.replace(day=1)
    elif time_filter == 'quarterly':
        start_date = today - timedelta(days=90)
    elif time_filter == 'yearly':
        start_date = today.replace(month=1, day=1)

    # Apply date filters if needed
    if apply_date_filter:
        date_range_filter = {'date__range': [
            start_date or (today - timedelta(days=90)), end_date]}
        transactions = transactions.filter(**date_range_filter)
        treatments = treatments.filter(appointment__date__range=[
                                       start_date or (today - timedelta(days=90)), end_date])
        payments = payments.filter(appointment__date__range=[
                                   start_date or (today - timedelta(days=90)), end_date])
        purchased_products = purchased_products.filter(
            appointment__date__range=[start_date or (today - timedelta(days=90)), end_date])
        patients = patients.filter(date_created__date__range=[
                                   start_date or (today - timedelta(days=90)), end_date])
        users = users.filter(date_joined__date__range=[
                             start_date or (today - timedelta(days=90)), end_date])
        products = products.filter(appointment__date__range=[
                                   start_date or (today - timedelta(days=90)), end_date])

    # Aggregations
    total_products_sold = purchased_products.aggregate(
        total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Income and Expenses (Top 5)
    income_data = transactions.filter(type="Income").values(
        'title').annotate(total=Sum('amount')).order_by('-total')[:5]
    income_dict = {item['title']: float(item['total']) for item in income_data}

    expense_data = transactions.filter(type="Expense").values(
        'title').annotate(total=Sum('amount')).order_by('-total')[:5]
    expense_dict = {item['title']: float(
        item['total']) for item in expense_data}

    # Treatment Counts
    treatment_types = [
        "Root Canals", "Dental Crowns", "Fillings", "Cleaning", "General Checkup",
        "Extractions", "Prosthetics", "Dental Implants", "Other"
    ]
    treatment_counts = {ttype: treatments.filter(
        treatment_type=ttype).count() for ttype in treatment_types}
    top_treatments = sorted(treatment_counts.items(),
                            key=lambda x: x[1], reverse=True)[:3]
    top_treatments_dict = dict(top_treatments)

    # Gender Distribution
    gender_counts = patients.values('gender').annotate(count=Count('id'))
    gender_dict = {item['gender'] or 'Unknown': item['count']
                   for item in gender_counts}

    context = {
        'page_title': 'Statistics',
        'active_page': 'statistics',
        'time_filter': time_filter,
        'date_range': date_range,
        'income_data': json.dumps(income_dict),
        'expense_data': json.dumps(expense_dict),
        'treatment_data': json.dumps(treatment_counts),
        'top_treatments': top_treatments_dict,
        'gender_data': json.dumps(gender_dict),
        'transactions': transactions,
        'treatments': treatments,
        'payments': payments,
        'purchased_products': purchased_products,
        'patients': patients,
        'users': users,
        'products': products,
        'total_products_sold': total_products_sold,
    }
    return render(request, 'statistics/statistics.html', context)


def error(request, exception):
    return render(request, 'error.html')


# api views

class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]


class MedicalHistoryViewSet(ModelViewSet):
    queryset = MedicalHistory.objects.select_related('patient')
    serializer_class = MedicalHistorySerializer
    permission_classes = [AllowAny]


class DentalChartViewSet(ModelViewSet):
    queryset = DentalChart.objects.select_related('patient')
    serializer_class = DentalChartSerializer
    permission_classes = [AllowAny]


class ToothRecordViewSet(ModelViewSet):
    queryset = ToothRecord.objects.select_related('dental_chart')
    serializer_class = ToothRecordSerializer
    permission_classes = [AllowAny]


class TreatmentPlanViewSet(ModelViewSet):
    queryset = TreatmentPlan.objects.select_related('patient')
    serializer_class = TreatmentPlanSerializer
    permission_classes = [AllowAny]


class TreatmentRecordViewSet(ModelViewSet):
    queryset = TreatmentRecord.objects.select_related('treatment_plan')
    serializer_class = TreatmentRecordSerializer
    permission_classes = [AllowAny]


class TreatmentDoctorViewSet(ModelViewSet):
    queryset = TreatmentDoctor.objects.select_related('doctor')
    serializer_class = TreatmentDoctorSerializer
    permission_classes = [AllowAny]


class PurchasedProductViewSet(ModelViewSet):
    queryset = PurchasedProduct.objects.select_related('appointment')
    serializer_class = PurchasedProductSerializer
    permission_classes = [AllowAny]


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.select_related('patient')
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.select_related('appointment')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.select_related('user')
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
