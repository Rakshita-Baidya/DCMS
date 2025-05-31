import re
from django.utils import timezone
from django import forms
from .models import (Patient, MedicalHistory, DentalChart, Payment,
                     ToothRecord, Transaction, Appointment, TreatmentPlan, TreatmentRecord, TreatmentDoctor, PurchasedProduct)
from users.models import User


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        exclude = ['patient']


class DentalChartForm(forms.ModelForm):
    class Meta:
        model = DentalChart
        fields = []


class ToothRecordForm(forms.ModelForm):
    TOOTH_NUMBERS = [str(i) for r in [range(11, 19), range(21, 29), range(31, 39), range(41, 49),
                                      range(51, 56), range(61, 66), range(71, 76), range(81, 86)]
                     for i in r]
    tooth_no = forms.ChoiceField(choices=[(num, num) for num in TOOTH_NUMBERS])

    class Meta:
        model = ToothRecord
        fields = '__all__'
        exclude = ['dental_chart']


ToothRecordFormSet = forms.inlineformset_factory(
    DentalChart, ToothRecord, form=ToothRecordForm, extra=0
)


class AppointmentForm(forms.ModelForm):
    patient_type = forms.ChoiceField(
        choices=[('existing', 'Existing Patient'), ('new', 'New Patient')],
        widget=forms.RadioSelect,
        initial='existing',
        label='Patient Type'
    )
    # Fields for new patient
    new_patient_name = forms.CharField(
        max_length=100, required=False, label='Patient Name')
    new_patient_contact = forms.CharField(
        max_length=17, required=False, label='Contact Number')
    new_patient_email = forms.EmailField(required=False, label='Email Address')
    new_patient_em_name = forms.CharField(
        max_length=100, required=False, label='Emergency Contact Name')
    new_patient_em_contact = forms.CharField(
        max_length=17, required=False, label='Emergency Contact Number')

    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'time',
                  'description', 'status', 'follow_up_days']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'patient': forms.Select(attrs={'required': False}),
        }

    def clean(self):
        cleaned_data = super().clean()
        patient_type = cleaned_data.get('patient_type')
        patient = cleaned_data.get('patient')
        new_patient_name = cleaned_data.get('new_patient_name')
        new_patient_contact = cleaned_data.get('new_patient_contact')
        new_patient_email = cleaned_data.get('new_patient_email')
        new_patient_em_name = cleaned_data.get('new_patient_em_name')
        new_patient_em_contact = cleaned_data.get('new_patient_em_contact')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if patient_type == 'existing':
            if not patient:
                self.add_error('patient', 'Please select an existing patient.')
            # Clear new patient fields
            cleaned_data['new_patient_name'] = ''
            cleaned_data['new_patient_contact'] = ''
            cleaned_data['new_patient_email'] = ''
            cleaned_data['new_patient_em_name'] = ''
            cleaned_data['new_patient_em_contact'] = ''
        else:  # new patient
            if not new_patient_name:
                self.add_error('new_patient_name',
                               'Name is required for new patients.')
            if not new_patient_contact:
                self.add_error('new_patient_contact',
                               'Contact number is required for new patients.')
            if not new_patient_email:
                self.add_error('new_patient_email',
                               'Email is required for new patients.')
            if not new_patient_em_name:
                self.add_error(
                    'new_patient_em_name', 'Emergency contact name is required for new patients.')
            if not new_patient_em_contact:
                self.add_error(
                    'new_patient_em_contact', 'Emergency contact number is required for new patients.')
            # Validate contact formats
            if new_patient_contact and not re.match(r'^\+?1?\d{9,15}$', new_patient_contact):
                self.add_error('new_patient_contact',
                               'Invalid contact number format.')
            if new_patient_em_contact and not re.match(r'^\+?1?\d{9,15}$', new_patient_em_contact):
                self.add_error('new_patient_em_contact',
                               'Invalid emergency contact number format.')
            # Check for duplicate email
            if new_patient_email and Patient.objects.filter(email=new_patient_email).exists():
                self.add_error('new_patient_email',
                               'This email is already registered.')
            # Clear existing patient field
            cleaned_data['patient'] = None

        # Check for pending appointments
        if patient_type == 'existing' and patient:
            # Check if the existing patient has a pending appointment
            pending_appointments = Appointment.objects.filter(
                patient=patient,
                status='Pending'
            ).exclude(id=self.instance.pk if self.instance else None)
            if pending_appointments.exists():
                self.add_error(
                    'patient', f'This patient already has a pending appointment on {pending_appointments.first().date} at {pending_appointments.first().time}.')
        elif patient_type == 'new' and new_patient_email:
            # Check if a patient with the new email already exists and has a pending appointment
            existing_patient = Patient.objects.filter(
                email=new_patient_email).first()
            if existing_patient:
                pending_appointments = Appointment.objects.filter(
                    patient=existing_patient,
                    status='Pending'
                ).exclude(id=self.instance.pk if self.instance else None)
                if pending_appointments.exists():
                    self.add_error(
                        'new_patient_email', f'A patient with this email already has a pending appointment on {pending_appointments.first().date} at {pending_appointments.first().time}.')

        if date and time:
            time = time.replace(microsecond=0)
            # Check for conflicting appointments
            conflicting = Appointment.objects.filter(
                date=date,
                time=time
            ).exclude(id=self.instance.pk if self.instance else None)

            if conflicting.exists():
                self.add_error('time', 'This time slot is already booked.')

        elif not time:
            self.add_error('time', 'Time is required.')

        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data['patient_type'] == 'new':
            # Create new patient
            patient = Patient.objects.create(
                name=self.cleaned_data['new_patient_name'],
                contact=self.cleaned_data['new_patient_contact'],
                email=self.cleaned_data['new_patient_email'],
                emergency_contact_name=self.cleaned_data['new_patient_em_name'],
                emergency_contact_contact=self.cleaned_data['new_patient_em_contact'],
                is_incomplete=True
            )
            self.instance.patient = patient
            if not self.instance.patient:
                raise forms.ValidationError(
                    "A patient must be selected or created before saving the appointment.")
        return super().save(commit=commit)


class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = '__all__'
        exclude = ['patient', 'last_updated']


class TreatmentRecordForm(forms.ModelForm):
    class Meta:
        model = TreatmentRecord
        fields = '__all__'
        exclude = ['appointment', 'date_created']


class TreatmentDoctorForm(forms.ModelForm):
    class Meta:
        model = TreatmentDoctor
        fields = '__all__'
        exclude = ['treatment_record', 'amount', 'date_created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='Doctor')
        self.fields['doctor'].label_from_instance = lambda obj: obj.get_full_name()


TreatmentDoctorFormSet = forms.inlineformset_factory(
    TreatmentRecord, TreatmentDoctor, form=TreatmentDoctorForm, extra=1, can_delete=True)


class PurchasedProductForm(forms.ModelForm):
    class Meta:
        model = PurchasedProduct
        fields = '__all__'
        exclude = ['appointment', 'total_amt', 'date_created']


PurchasedProductFormSet = forms.inlineformset_factory(
    Appointment, PurchasedProduct, form=PurchasedProductForm, extra=1, can_delete=True)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        exclude = ['appointment', 'final_amount',
                   'remaining_balance', 'payment_status']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['user', 'date_created']
