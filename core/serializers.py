from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    Patient, MedicalHistory, DentalChart, ToothRecord,
    Appointment, TreatmentPlan, TreatmentRecord, TreatmentDoctor, PurchasedProduct,
    Payment, Transaction, User
)

# Patient Serializer


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['date_created']

    def validate_age(self, value):
        if value and value > 150:
            raise serializers.ValidationError("Age cannot exceed 150.")
        return value

    def validate_contact(self, value):
        if not value:
            raise serializers.ValidationError("Contact number is required.")
        return value

# Medical History Serializer


class MedicalHistorySerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'

    def validate_rheumatic_fever_age(self, value):
        if value and value > 100:
            raise serializers.ValidationError(
                "Rheumatic fever age cannot exceed 100.")
        return value


# Dental Chart Serializer


class ToothRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToothRecord
        fields = '__all__'


class DentalChartSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    tooth_records = ToothRecordSerializer(many=True, read_only=True)

    class Meta:
        model = DentalChart
        fields = '__all__'

# Appointment Serializer


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['date_created']

# Treatment Plan Serializer


class TreatmentPlanSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = '__all__'

# Treatment Record Serializer


class TreatmentRecordSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = TreatmentRecord
        fields = '__all__'
        read_only_fields = ['date_created']

# Treatment Doctor Serializer


class TreatmentDoctorSerializer(serializers.ModelSerializer):
    treatment_record = TreatmentRecordSerializer(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = TreatmentDoctor
        fields = '__all__'
        read_only_fields = ['date_created']

    def validate_percent(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Percent must be between 0 and 100.")
        return value

# Purchased Product Serializer


class PurchasedProductSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = PurchasedProduct
        fields = '__all__'
        read_only_fields = ['total_amt', 'date_created']

    def validate(self, data):
        if 'rate' in data and 'quantity' in data:
            data['total_amt'] = data['rate'] * data['quantity']
        return data

# Payment Serializer


class PaymentSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['remaining_balance',
                            'payment_status', 'date_created']

    def validate(self, data):
        if 'final_amount' in data and 'paid_amount' in data:
            data['remaining_balance'] = data['final_amount'] - \
                data['paid_amount']
            if data['remaining_balance'] > 0:
                data['payment_status'] = 'Pending'
            elif data['remaining_balance'] == 0:
                data['payment_status'] = 'Paid'
            else:
                data['payment_status'] = 'Overpaid'
        return data

# Transaction Serializer


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['date_created']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value
