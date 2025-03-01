from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import AdminOnly, AllowedUsers, UnauthenticatedUser
from django.core.files.storage import FileSystemStorage
import os
from django.forms import formset_factory
from datetime import date

from formtools.wizard.views import SessionWizardView
from django.urls import reverse

from users.models import User
from users.forms import UserEditForm
from users.serializers import UserSerializer

from .models import Patient, MedicalHistory, OtherPatientHistory, DentalChart, Payment, ToothRecord, Appointment, TreatmentPlan, TreatmentRecord, TreatmentDoctor, PurchasedProduct, Transaction
from .forms import (AppointmentForm, PatientForm,  MedicalHistoryForm,
                    OtherPatientHistoryForm, DentalChartForm, PaymentForm, PurchasedProductFormSet, ToothRecordFormSet, TreatmentDoctorForm, TreatmentDoctorFormSet, TreatmentPlanForm, TreatmentRecordForm)

from .serializers import PatientSerializer, MedicalHistorySerializer, OtherPatientHistorySerializer, AppointmentSerializer, ToothRecordSerializer, DentalChartSerializer, PaymentSerializer, TransactionSerializer, TreatmentPlanSerializer, TreatmentDoctorSerializer, TreatmentRecordSerializer, PurchasedProductSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

# api views


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]


class MedicalHistoryViewSet(ModelViewSet):
    queryset = MedicalHistory.objects.select_related('patient')
    serializer_class = MedicalHistorySerializer
    permission_classes = [AllowAny]


class OtherPatientHistoryViewSet(ModelViewSet):
    queryset = OtherPatientHistory.objects.select_related('history')
    serializer_class = OtherPatientHistorySerializer
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


# Create your views here.


@login_required(login_url='login')
def dashboard(request):
    patient_queryset = Patient.objects.all().order_by('id')

    appointment_queryset = Appointment.objects.filter(date=date.today())
    completed_appointments = Appointment.objects.filter(
        status='Completed')

    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'total_patient': patient_queryset.count(),
        'appointments': appointment_queryset,
        'completed_appointments': completed_appointments.count(),
        'total_appointment': appointment_queryset.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


@AllowedUsers(allowed_roles=['Administrator'])
@login_required(login_url='login')
def doctor(request):
    doctor_queryset = User.objects.filter(role='Doctor')

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
        treatments__treatment_td__doctor=doctor_queryset).distinct().order_by('-date', '-time')[:5]

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
    staff_queryset = User.objects.filter(role='Staff')

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
            Q(patient__name__icontains=search_query) |
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


class AppointmentFormWizard(SessionWizardView):
    form_list = [AppointmentForm, TreatmentRecordForm,
                 TreatmentDoctorFormSet, PurchasedProductFormSet]
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

        messages.success(
            request, 'The appointment has been added successfully!')
        return redirect('core:appointment')


class EditAppointmentWizard(SessionWizardView):
    form_list = [AppointmentForm, TreatmentRecordForm,
                 TreatmentDoctorFormSet, PurchasedProductFormSet]
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
        appointment_id = self.kwargs.get('appointment_id')

        context.update({
            'page_title': 'Appointment Management',
            'active_page': 'appointment',
            'patients': Patient.objects.all(),
            'doctors': User.objects.filter(role='Doctor'),
            'is_editing': bool(appointment_id),
        })

        # Handle formsets directly in context
        if self.steps.current == '2':
            # For TreatmentDoctorFormSet
            treatment = None
            if appointment_id:
                appointment = get_object_or_404(Appointment, id=appointment_id)
                treatment = TreatmentRecord.objects.filter(
                    appointment=appointment).first()

            context['treatment_doctor_formset'] = form
            if isinstance(form, TreatmentDoctorFormSet):
                if self.storage.get_step_data('2'):
                    form.initial = self.storage.get_step_data('2')
                context['treatment_doctor_formset'] = form

        elif self.steps.current == '3':
            # For PurchasedProductFormSet
            if appointment_id:
                appointment = get_object_or_404(Appointment, id=appointment_id)
                context['purchased_product_formset'] = form
                if isinstance(form, PurchasedProductFormSet):
                    if self.storage.get_step_data('3'):
                        form.initial = self.storage.get_step_data('3')
                    context['purchased_product_formset'] = form

        return context

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)

        appointment_id = self.kwargs.get('appointment_id')
        if appointment_id:
            appointment = get_object_or_404(Appointment, id=appointment_id)

            if step == '2':
                treatment = TreatmentRecord.objects.filter(
                    appointment=appointment).first()
                if isinstance(form, TreatmentDoctorFormSet):
                    if treatment:
                        form.instance = treatment
            elif step == '3':
                if isinstance(form, PurchasedProductFormSet):
                    form.instance = appointment

        return form

    def get_form_instance(self, step):
        appointment_id = self.kwargs.get('appointment_id')
        if not appointment_id:
            return None

        appointment = get_object_or_404(Appointment, id=appointment_id)

        if step == '0':
            return appointment
        elif step == '1':
            treatment = TreatmentRecord.objects.filter(
                appointment=appointment).first()
            if not treatment:
                treatment = TreatmentRecord(appointment=appointment)
            return treatment
        elif step == '2':
            treatment = TreatmentRecord.objects.filter(
                appointment=appointment).first()
            if not treatment:
                treatment = TreatmentRecord(appointment=appointment)
                treatment.save()
            return treatment
        elif step == '3':
            return appointment
        return None

    def done(self, form_list, **kwargs):
        request = self.request
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Save Appointment data
        appointment_form = form_list[0]
        for field, value in appointment_form.cleaned_data.items():
            setattr(appointment, field, value)
        appointment.save()

        # Save Treatment data
        treatment_form = form_list[1]
        treatment = TreatmentRecord.objects.filter(
            appointment=appointment).first()
        if not treatment:
            treatment = TreatmentRecord(appointment=appointment)

        for field, value in treatment_form.cleaned_data.items():
            setattr(treatment, field, value)
        treatment.save()

        # Save multiple TreatmentDoctor records
        treatment_doctor_formset = form_list[2]
        if treatment_doctor_formset.is_valid():
            treatment_doctor_formset.instance = treatment
            treatment_doctor_formset.save()

        # Save multiple PurchasedProduct records
        purchased_product_formset = form_list[3]
        if purchased_product_formset.is_valid():
            purchased_product_formset.instance = appointment
            purchased_product_formset.save()

        messages.success(
            request, 'The appointment has been updated successfully!')
        return redirect('core:appointment')


@login_required(login_url='login')
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    # Get related data
    purchased_products = PurchasedProduct.objects.filter(
        appointment=appointment)

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
        # 'treatment': treatment,
        # 'treatment_doctors': treatment_doctors,
        'purchased_products': purchased_products,
    }

    return render(request, 'appointment/view_appointment.html', context)


@login_required(login_url='login')
def schedule(request):
    appointments = Appointment.objects.all()
    appointments_data = [
        {
            'title': f"Appointment - {app.patient.name}",
            'start': f"{app.date.isoformat()}T{app.time}",
            'extendedProps': {
                'patient_name': app.patient.name,
                'description': app.description or 'No description provided',
                'status': app.status,
            }
        }
        for app in appointments
    ]

    # # Add search functionality
    # search_query = request.GET.get('search', '')
    # if search_query:
    #     appointment_queryset = appointments.filter(
    #         Q(patient__name__icontains=search_query) |
    #         Q(description__icontains=search_query)
    #     )

    context = {
        'page_title': 'Schedule Management',
        'active_page': 'schedule',
        'appointments': appointments_data,
    }
    return render(request, 'schedule/schedule.html', context)


@login_required(login_url='login')
@AdminOnly
def finance(request):
    context = {
        'page_title': 'Finance Management',
        'active_page': 'finance',
    }
    return render(request, 'finance/finance.html', context)


@login_required(login_url='login')
@AdminOnly
def statistics(request):
    context = {
        'page_title': 'Statistics',
        'active_page': 'statistics',
    }
    return render(request, 'statistics/statistics.html', context)


def error(request):
    return render(request, 'error.html')
