from django import forms
from .models import (Patient, MedicalHistory, OtherPatientHistory, DentalChart,
                     ToothRecord, Transaction, Appointment, Treatment, TreatmentDoctor, PurchasedProduct)


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


TreatmentDoctorFormSet = forms.inlineformset_factory(
    Treatment, TreatmentDoctor, form=TreatmentDoctorForm, extra=0
)


class PurchasedProductForm(forms.ModelForm):
    class Meta:
        model = PurchasedProduct
        fields = '__all__'
        exclude = ['appointment']


PurchasedProductFormSet = forms.inlineformset_factory(
    Appointment, PurchasedProduct, form=PurchasedProductForm, extra=0)
