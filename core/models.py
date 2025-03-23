from datetime import timedelta
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.db import models

from users.models import User

# Create your models here.
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

MARTIAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Widowed', 'Widowed'),
    ('Other', 'Other'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Prefer not to say', 'Prefer not to say'),
    ('Other', 'Other'),
]

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-')
]


class Patient(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(
        validators=[phone_regex], max_length=17)
    address = models.CharField(max_length=150, blank=True, null=True)
    # dob = models.DateField(default=now,
    #                        blank=True, null=True)
    gender = models.CharField(max_length=17, null=True, blank=True,
                              default="Prefer not to say", choices=GENDER_CHOICES)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES)
    age = models.PositiveIntegerField(
        blank=True, null=True, validators=[MaxValueValidator(150)])
    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=10, blank=True, null=True)
    occupation = models.CharField(blank=True, null=True)
    nationality = models.CharField(blank=True, null=True)
    marital_status = models.CharField(choices=MARTIAL_STATUS, default="Single")
    reffered_by = models.CharField(max_length=50, blank=True, null=True)
    # profile_image = models.ImageField(
    #     upload_to='images/patient/',
    #     default='images/profile/default.jpg',
    #     blank=True,
    #     null=True,
    # )
    emergency_contact_name = models.CharField(
        max_length=100)
    emergency_contact_contact = models.CharField(
        validators=[phone_regex], max_length=13)
    emergency_contact_address = models.CharField(
        max_length=150, blank=True, null=True)
    emergency_contact_relation = models.CharField(
        max_length=15, blank=True, null=True)

    date_created = models.DateTimeField(default=now,
                                        blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class MedicalHistory(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='patient_history')
    chief_dental_complaint = models.TextField(blank=True, null=True)
    marked_weight_change = models.BooleanField(default=False)

    # heart
    chest_pain = models.BooleanField(default=False)
    hypertention = models.BooleanField(default=False)
    ankle_edema = models.BooleanField(default=False)
    rheumatic_fever = models.BooleanField(default=False)
    rheumatic_fever_age = models.PositiveBigIntegerField(
        validators=[MaxValueValidator(100)], blank=True, null=True)
    stroke_history = models.BooleanField(default=False)
    stroke_date = models.DateField(blank=True, null=True)

    # arthritis
    joint_pain = models.BooleanField(default=False)
    joint_swelling = models.BooleanField(default=False)

    # nervous system
    headaches = models.BooleanField(default=False)
    convulsions_or_epilepsy = models.BooleanField(default=False)
    numbness_or_tingles = models.BooleanField(default=False)
    dizziness_or_fainting = models.BooleanField(default=False)

    # liver
    jaundice = models.BooleanField(default=False)
    history_of_liver_disease = models.BooleanField(default=False)
    liver_disease_specifics = models.TextField(
        max_length=500, blank=True, null=True)

    # women
    pregnancy = models.BooleanField(default=False)
    pregnancy_month = models.CharField(max_length=2, blank=True, null=True)
    breast_feed = models.BooleanField(default=False)

    # respiratory
    persistant_cough = models.BooleanField(default=False)
    breathing_difficulty = models.BooleanField(default=False)
    shortness_of_breath = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)

    # ear
    hearing_loss = models.BooleanField(default=False)
    ringing_of_ears = models.BooleanField(default=False)

    # blood
    bruise_easy = models.BooleanField(default=False)
    anemia = models.BooleanField(default=False)

    # thyroid
    perspire_easy = models.BooleanField(default=False)
    apprehension = models.BooleanField(default=False)
    palpitation = models.BooleanField(default=False)
    goiter = models.BooleanField(default=False)
    bulging_eyes = models.BooleanField(default=False)

    # diabetes
    delayed_healing = models.BooleanField(default=False)
    increased_appetite = models.BooleanField(default=False)
    family_history = models.BooleanField(default=False)

    # radiography
    radiography_therapy = models.BooleanField(default=False)

    # urinary
    increased_frequency = models.BooleanField(default=False)
    burning = models.BooleanField(default=False)

    # extraction
    prev_extraction = models.BooleanField(default=False)
    date_of_last_extraction = models.DateField(blank=True, null=True)
    untoward_reaction = models.BooleanField(default=False)
    untoward_reaction_specifics = models.TextField(
        max_length=500, blank=True, null=True)
    local_anesthesia_use = models.BooleanField(default=False)

    # hospitalization
    hospitalized = models.BooleanField(default=False)
    admission_date = models.DateField(blank=True, null=True)
    hospitalization_specifics = models.TextField(
        max_length=500, blank=True, null=True)

    # allergies
    sleeping_pills = models.BooleanField(default=False)
    aspirin = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    penicilin = models.BooleanField(default=False)
    antibiotics = models.BooleanField(default=False)
    sulfa_drugs = models.BooleanField(default=False)
    local_anesthesia = models.BooleanField(default=False)
    others = models.BooleanField(default=False)
    specifics = models.TextField(max_length=500, blank=True, null=True)

    # habits
    smoking = models.BooleanField(default=False)
    tobacco_chewing = models.BooleanField(default=False)
    alcohol = models.BooleanField(default=False)
    betel_nuts = models.BooleanField(default=False)
    paan_chewing = models.BooleanField(default=False)

    # oral hygiene
    stain = models.BooleanField(default=False)
    calculus = models.BooleanField(default=False)
    halitosis = models.BooleanField(default=False)

    def __str__(self):
        return f"Medical History for {self.patient.name}"


class DentalChart(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='dental_chart')

    def __str__(self):
        return f"Dental Chart for {self.patient.name}"


SEVERITY_CHOICES = [
    ('Mild', 'Mild'),
    ('Moderate', 'Moderate'),
    ('Severe', 'Severe')
]


class ToothRecord(models.Model):
    dental_chart = models.ForeignKey(
        DentalChart, on_delete=models.CASCADE, related_name='tooth_records')
    tooth_no = models.CharField(max_length=10)
    description = models.TextField(max_length=255, blank=True, null=True)
    condition = models.CharField(
        choices=SEVERITY_CHOICES, max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Tooth {self.tooth_no} - ({self.severity})"


APPOINTMENT_STATUS = [
    ('Pending', 'Pending'),
    ('Cancelled', 'Cancelled'),
    ('Completed', 'Completed')
]


class Appointment(models.Model):
    patient = models.ForeignKey(
        'Patient', on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField(default=timezone.now)
    time = models.TimeField()
    description = models.TextField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=APPOINTMENT_STATUS, default="Pending")
    follow_up_days = models.PositiveIntegerField(
        blank=True, null=True, validators=[MaxValueValidator(365)],
    )
    date_created = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'date', 'time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'date', 'time'], name='unique_patient_appointment')
        ]

    def get_follow_up_date(self):
        if self.follow_up_days is not None:
            return self.date + timedelta(days=self.follow_up_days)
        return None

    def __str__(self):
        return f"{self.patient.name} - {self.date} {self.time} ({self.status})"


LAB_CHOICES = [
    ('Medi Dent Nepal', 'Medi Dent Nepal'),
    ('Proficient Dental Lab', 'Proficient Dental Lab'),
    ('Other', 'Other')]

TREATMENT_CHOICES = [
    ('General Checkup', 'General Checkup'),
    ('Cleaning', 'Cleaning'),
    ('Fillings', 'Fillings'),
    ('Extractions', 'Extractions'),
    ('Prosthetics', 'Prosthetics'),
    ('Dental Implants', 'Dental Implants'),
    ('Root Canals', 'Root Canals'),
    ('Dental Crowns', 'Dental Crowns'),
    ('Other', 'Other')]


class TreatmentPlan(models.Model):
    patient = models.OneToOneField(
        'Patient', on_delete=models.CASCADE, related_name='treatment_plan')
    treatment_plan = models.TextField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Treatment Plan for {self.patient.name}"


class TreatmentRecord(models.Model):
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='treatment_records')
    treatment_type = models.CharField(
        max_length=100, blank=True, null=True, choices=TREATMENT_CHOICES)
    x_ray = models.BooleanField(default=False)
    x_ray_cost = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True, validators=[MinValueValidator(0)])
    lab = models.BooleanField(default=False)
    lab_sent = models.CharField(
        max_length=50, choices=LAB_CHOICES, blank=True, null=True)
    lab_order_date = models.DateTimeField(blank=True, null=True)
    lab_cost = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_cost = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True, validators=[MinValueValidator(0)])
    date_created = models.DateTimeField(
        default=timezone.now, blank=True, null=True)

    def clean(self):
        if self.lab and not self.lab_sent:
            raise ValidationError("Lab sent must be specified if lab is True.")
        if not self.lab and self.lab_sent:
            self.lab_sent = None

    def __str__(self):
        return f"{self.treatment_type or 'Treatment'} for {self.appointment.patient.name} on {self.appointment.date}"


class TreatmentDoctor(models.Model):
    treatment_record = models.ForeignKey(
        TreatmentRecord, on_delete=models.CASCADE, related_name='doctors')
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='treatment_assignments')
    percent = models.DecimalField(decimal_places=2, max_digits=5,
                                  validators=[MinValueValidator(0), MaxValueValidator(100)])
    amount = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    date_created = models.DateTimeField(
        default=timezone.now, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.treatment_record.treatment_cost and self.percent:
            self.amount = (self.treatment_record.treatment_cost *
                           self.percent) / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.doctor.username} - {self.treatment_record.appointment.patient.name} ({self.percent}%)"


class PurchasedProduct(models.Model):
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='purchased_products')
    name = models.CharField(max_length=100)
    rate = models.DecimalField(
        decimal_places=2, max_digits=10, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_amt = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.rate is not None and self.quantity is not None:
            self.total_amt = self.rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.quantity} pcs) for {self.appointment.patient.name} on {self.appointment.date}"


PAYMENT_METHOD_CHOICES = [
    ('Cash', 'Cash'),
    ('Card', 'Card'),
    ('Mobile Payment', 'Mobile Payment'),
    ('Bank Transfer', 'Bank Transfer'),
    ('Other', 'Other'),
]


class Payment(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='payment')
    additional_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    final_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    remaining_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=15, default="Unpaid")
    payment_method = models.CharField(
        max_length=15, choices=PAYMENT_METHOD_CHOICES, default="Cash", blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(
        default=timezone.now, blank=True, null=True)

    def calculate_final_amount(self):
        treatment_cost = sum(
            tr.treatment_cost or 0 for tr in self.appointment.treatment_records.all()
        ) + sum(
            tr.x_ray_cost or 0 for tr in self.appointment.treatment_records.all() if tr.x_ray
        ) + sum(
            tr.lab_cost or 0 for tr in self.appointment.treatment_records.all() if tr.lab
        )
        product_cost = sum(
            pp.total_amt or 0 for pp in self.appointment.purchased_products.all()
        )
        return (treatment_cost + product_cost + self.additional_cost) - self.discount_amount

    def save(self, *args, **kwargs):
        self.final_amount = self.calculate_final_amount()
        self.remaining_balance = self.final_amount - self.paid_amount
        if self.remaining_balance > 0:
            self.payment_status = 'Pending'
        elif self.remaining_balance == 0:
            self.payment_status = 'Paid'
        else:
            self.payment_status = 'Overpaid'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.appointment.patient.name} - {self.appointment.date} ({self.payment_status})"


TRANSACTION_TYPE = [
    ('Income', 'Income'),
    ('Expense', 'Expense'),
]


class Transaction(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='transaction_user')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=now)
    type = models.CharField(choices=TRANSACTION_TYPE, default="Income")
    date_created = models.DateTimeField(default=now, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.title} ({self.type})"
