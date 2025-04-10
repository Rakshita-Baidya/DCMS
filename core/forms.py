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
    class Meta:
        model = Appointment
        fields = '__all__'
        exclude = ['date_created']


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
