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
