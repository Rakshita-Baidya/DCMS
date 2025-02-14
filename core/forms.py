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
        exclude = ['patient']


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


class NervousHistoryForm(forms.ModelForm):
    class Meta:
        model = NervousHistory
        fields = '__all__'
        exclude = ['history']


class WomenHistoryForm(forms.ModelForm):
    class Meta:
        model = WomenHistory
        fields = '__all__'
        exclude = ['history']


class LiverHistoryForm(forms.ModelForm):
    class Meta:
        model = LiverHistory
        fields = '__all__'
        exclude = ['history']


class RadiographyHistoryForm(forms.ModelForm):
    class Meta:
        model = RadiographyHistory
        fields = '__all__'
        exclude = ['history']


class RespitoryHistoryForm(forms.ModelForm):
    class Meta:
        model = RespitoryHistory
        fields = '__all__'
        exclude = ['history']


class BloodHistoryForm(forms.ModelForm):
    class Meta:
        model = BloodHistory
        fields = '__all__'
        exclude = ['history']


class DiabetesHistoryForm(forms.ModelForm):
    class Meta:
        model = DiabetesHistory
        fields = '__all__'
        exclude = ['history']


class ThyroidHistoryForm(forms.ModelForm):
    class Meta:
        model = ThyroidHistory
        fields = '__all__'
        exclude = ['history']


class UrinaryHistoryForm(forms.ModelForm):
    class Meta:
        model = UrinaryHistory
        fields = '__all__'
        exclude = ['history']


class ExtractionHistoryForm(forms.ModelForm):
    class Meta:
        model = ExtractionHistory
        fields = '__all__'
        exclude = ['history']


class AllergiesHistoryForm(forms.ModelForm):
    class Meta:
        model = AllergiesHistory
        fields = '__all__'
        exclude = ['history']


class HospitalizationHistoryForm(forms.ModelForm):
    class Meta:
        model = HospitalizationHistory
        fields = '__all__'
        exclude = ['history']
