from django import forms
from .models import (Patient, MedicalHistory, HeartHistory, HospitalizationHistory, EarHistory, EmergencyContact, ArthritisHistory, NervousHistory, WomenHistory,
                     LiverHistory, RadiographyHistory, RespitoryHistory, ExtractionHistory, BloodHistory, AllergiesHistory, DiabetesHistory, ThyroidHistory, UrinaryHistory)


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = '__all__'


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        exclude = ['patient']


class HeartHistoryForm(forms.ModelForm):
    class Meta:
        model = HeartHistory
        fields = '__all__'
        exclude = ['history']


class HospitalizationHistoryForm(forms.ModelForm):
    class Meta:
        model = HospitalizationHistory
        fields = '__all__'
        exclude = ['history']


class EarHistoryForm(forms.ModelForm):
    class Meta:
        model = EarHistory
        fields = '__all__'
        exclude = ['history']


class ArthritisHistoryForm(forms.ModelForm):
    class Meta:
        model = ArthritisHistory
        fields = '__all__'
        exclude = ['history']
