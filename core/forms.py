from django import forms
from .models import *
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


class OtherPatientHistoryForm(forms.ModelForm):
    class Meta:
        model = OtherPatientHistory
        fields = '__all__'
        exclude = ['history']


class DentalChartForm(forms.ModelForm):
    class Meta:
        model = DentalChart
        fields = []


class ToothRecordForm(forms.ModelForm):
    class Meta:
        model = ToothRecord
        fields = '__all__'
        exclude = ['dental_chart']


ToothRecordFormSet = forms.inlineformset_factory(
    DentalChart, ToothRecord, form=ToothRecordForm, extra=0
)


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'


class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = '__all__'
        exclude = ['patient']


class TreatmentRecordForm(forms.ModelForm):
    class Meta:
        model = TreatmentRecord
        fields = '__all__'
        exclude = ['appointment']


class TreatmentDoctorForm(forms.ModelForm):
    class Meta:
        model = TreatmentDoctor
        fields = '__all__'
        exclude = ['treatment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow users who have a doctor_profile
        self.fields['doctor'].queryset = User.objects.filter(
            role='Doctor', doctor_profile__isnull=False)
        self.fields['doctor'].label_from_instance = lambda obj: obj.get_full_name()


TreatmentDoctorFormSet = forms.inlineformset_factory(
    TreatmentRecord, TreatmentDoctor, form=TreatmentDoctorForm, extra=1, can_delete=True)


class PurchasedProductForm(forms.ModelForm):
    class Meta:
        model = PurchasedProduct
        fields = '__all__'
        exclude = ['appointment', 'total_amt']


PurchasedProductFormSet = forms.inlineformset_factory(
    Appointment, PurchasedProduct, form=PurchasedProductForm, extra=1, can_delete=True)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        exclude = ['appointment']
        widgets = {
            'final_amount': forms.HiddenInput(),
            'remaining_balance': forms.HiddenInput(),
            'payment_status': forms.HiddenInput(),
        }
