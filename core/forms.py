from django import forms
from .models import Patient, MedicalHistory, HeartHistory, HospitalizationHistory, EarHistory, EmergencyContact, ArthritisHistory, NervousHistory, WomenHistory, LiverHistory, RadiographyHistory, RespitoryHistory, ExtractionHistory, BloodHistory, AllergiesHistory, DiabetesHistory, ThyroidHistory, UrinaryHistory


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
