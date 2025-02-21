from django import forms
from .models import (Patient, MedicalHistory, OtherPatientHistory, DentalChart,
                     ToothRecord, Transaction, Appointment, Treatment, TreatmentDoctor, PurchasedProduct)
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


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
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
    Treatment, TreatmentDoctor, form=TreatmentDoctorForm, extra=1, can_delete=True)


class PurchasedProductForm(forms.ModelForm):
    class Meta:
        model = PurchasedProduct
        fields = '__all__'
        exclude = ['appointment', 'total_amt']


PurchasedProductFormSet = forms.inlineformset_factory(
    Appointment, PurchasedProduct, form=PurchasedProductForm, extra=1, can_delete=True)
