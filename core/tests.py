from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Patient, MedicalHistory, Appointment, Transaction
from core.forms import PatientForm, MedicalHistoryForm, AppointmentForm, TransactionForm
from datetime import datetime
import json

User = get_user_model()


class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='admin', password='admin123', role='Administrator', email='admin@example.com'
        )
        self.client.login(username='admin', password='admin123')
        self.patient = Patient.objects.create(
            name='John Doe',
            contact='+1234567890',
            blood_group='O+',
            emergency_contact_name='Jane Doe',
            emergency_contact_contact='+0987654321'
        )

    def test_add_patient_empty_emergency_name(self):
        form_data = {
            'name': 'Jane Smith',
            'contact': '+1234567890',
            'blood_group': 'A+',
            'emergency_contact_name': '',
            'emergency_contact_contact': '+0987654321'
        }
        form = PatientForm(data=form_data)
        print(f"Test 4: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('emergency_contact_name', form.errors)
        self.assertEqual(
            form.errors['emergency_contact_name'][0], 'This field is required.')

    def test_save_patient_invalid_allergy_field(self):
        form_data = {
            'chief_dental_complaint': 'Toothache',
            'specifics': 'A' * 501
        }
        form = MedicalHistoryForm(data=form_data)
        print(f"Test 5: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('specifics', form.errors)
        self.assertEqual(
            form.errors['specifics'][0], 'Ensure this value has at most 500 characters (it has 501).')

    def test_schedule_appointment_null_patient(self):
        form_data = {
            'date': timezone.now().date(),
            'time': '10:00:00',
            'status': 'Pending'
        }
        form = AppointmentForm(data=form_data)
        print(f"Test 6: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        self.assertEqual(form.errors['patient'][0],
                         'This field is required.')

    def test_create_appointment_invalid_date(self):
        form_data = {
            'patient': self.patient.id,
            'date': '2025-13-01',  # Invalid monthS
            'time': '10:00:00',
            'status': 'Pending'
        }
        form = AppointmentForm(data=form_data)
        print(f"Test 7: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
        self.assertEqual(form.errors['date'][0], 'Enter a valid date.')

    def test_add_income_negative_amount(self):
        form_data = {
            'title': 'Income Test',
            'amount': -100,
            'date': timezone.now().date(),
            'time': '10:00:00',
            'type': 'Income'
        }
        form = TransactionForm(data=form_data)
        print(f"Test 8: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(
            form.errors['amount'][0], 'Ensure this value is greater than or equal to 1.')

    def test_add_expense_negative_amount(self):
        form_data = {
            'title': 'Expense Test',
            'amount': -50,
            'date': timezone.now().date(),
            'time': '10:00:00',
            'type': 'Expense'
        }
        form = TransactionForm(data=form_data)
        print(f"Test 9: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(
            form.errors['amount'][0], 'Ensure this value is greater than or equal to 1.')
        
    def test_generate_report_missing_data(self):
        patient = Patient.objects.create(
            name='Minimal Patient',
            contact='+1234567890',
            blood_group='A+',
            emergency_contact_name='Test Contact',
            emergency_contact_contact='+0987654321'
        )
        response = self.client.get(
            reverse('core:generate_patient_pdf', args=[patient.id]))
        print(
            f"Test 15: Response status: {response.status_code}, Content-Type: {response['Content-Type']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
