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
        fields = [
            'id', 'name', 'contact', 'address', 'gender', 'blood_group', 'age', 'email',
            'telephone', 'occupation', 'nationality', 'marital_status', 'reffered_by',
            'emergency_contact_name', 'emergency_contact_contact', 'emergency_contact_address',
            'emergency_contact_relation', 'date_created'
        ]
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
        fields = [
            'id', 'patient', 'chief_dental_complaint', 'marked_weight_change',
            'chest_pain', 'hypertention', 'ankle_edema', 'rheumatic_fever', 'rheumatic_fever_age',
            'stroke_history', 'stroke_date', 'joint_pain', 'joint_swelling', 'headaches',
            'convulsions_or_epilepsy', 'numbness_or_tingles', 'dizziness_or_fainting',
            'jaundice', 'history_of_liver_disease', 'liver_disease_specifics', 'pregnancy',
            'pregnancy_month', 'breast_feed', 'persistant_cough', 'breathing_difficulty',
            'shortness_of_breath', 'asthma', 'hearing_loss', 'ringing_of_ears', 'bruise_easy',
            'anemia', 'perspire_easy', 'apprehension', 'palpitation', 'goiter', 'bulging_eyes',
            'delayed_healing', 'increased_appetite', 'family_history', 'radiography_therapy',
            'increased_frequency', 'burning', 'prev_extraction', 'date_of_last_extraction', 'untoward_reaction',
            'untoward_reaction_specifics', 'local_anesthesia_use', 'hospitalized', 'admission_date',
            'hospitalization_specifics', 'sleeping_pills', 'aspirin', 'food', 'penicilin',
            'antibiotics', 'sulfa_drugs', 'local_anesthesia', 'others', 'specifics', 'smoking',
            'tobacco_chewing', 'alcohol', 'betel_nuts', 'paan_chewing', 'stain', 'calculus',
            'halitosis'
        ]

    def validate_rheumatic_fever_age(self, value):
        if value and value > 100:
            raise serializers.ValidationError(
                "Rheumatic fever age cannot exceed 100.")
        return value


# Dental Chart Serializer


class ToothRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToothRecord
        fields = ['id', 'tooth_no', 'description', 'condition']


class DentalChartSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    tooth_records = ToothRecordSerializer(many=True, read_only=True)

    class Meta:
        model = DentalChart
        fields = ['id', 'patient', 'tooth_records']

# Appointment Serializer


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'date', 'time',
                  'description', 'status', 'date_created']
        read_only_fields = ['date_created']

# Treatment Plan Serializer


class TreatmentPlanSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = ['id', 'patient', 'treatment_plan']

# Treatment Record Serializer


class TreatmentRecordSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = TreatmentRecord
        fields = [
            'id', 'appointment', 'type', 'x_ray', 'x_ray_cost', 'lab', 'lab_sent',
            'lab_order_date', 'lab_cost', 'treatment_cost', 'date_created'
        ]
        read_only_fields = ['date_created']

# Treatment Doctor Serializer


class TreatmentDoctorSerializer(serializers.ModelSerializer):
    treatment_record = TreatmentRecordSerializer(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = TreatmentDoctor
        fields = ['id', 'treatment_record', 'doctor',
                  'percent', 'amount', 'date_created']
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
        fields = ['id', 'appointment', 'name', 'rate',
                  'quantity', 'total_amt', 'date_created']
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
        fields = [
            'id', 'appointment', 'additional_cost', 'discount_amount', 'paid_amount',
            'final_amount', 'remaining_balance', 'payment_status', 'payment_method',
            'payment_date', 'payment_notes', 'date_created'
        ]
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
        fields = ['id', 'user', 'title',
                  'description', 'amount', 'date', 'type']
        read_only_fields = ['date']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value
