from django.utils.timezone import now
from django.db import models
from users.models import User

# Create your models here.
TRANSACTION_TYPE = [
    ('Income', 'Income'),
    ('Expense', 'Expense'),
    ('Payment', 'Payment'),
]

MARTIAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Widowed', 'Widowed'),
    ('Other', 'Other'),
]


class Transaction(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='transaction_profile')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=now)
    type = models.CharField(choices=TRANSACTION_TYPE, default="Income")

    def __str__(self):
        return super().__str__()


class Patient(models.Model):
    reg_no = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=150, blank=True, null=True)
    dob = models.DateField(default=now,
                           blank=True, null=True)
    gender = models.CharField(max_length=6)
    blood_group = models.CharField(max_length=3)
    age = models.CharField(max_length=3)
    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=10)
    occupation = models.CharField(blank=True, null=True)
    nationality = models.CharField(blank=True, null=True)
    marital_status = models.CharField(choices=MARTIAL_STATUS, default="Single")
    profile_image = models.ImageField(
        upload_to='images/profile/',
        default='images/profile/default.jpg',
        blank=True,
        null=True,
    )

    def __str__(self):
        return super().__str__()


class EmergencyContact(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='patient_emergency')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=150, blank=True, null=True)
    relation = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return super().__str__()


class MedicalHistory(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='patient_history')
    chief_dental_complaint = models.CharField(
        max_length=500, blank=True, null=True)
    marked_weight_change = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class HeartHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_heart')
    chest_pain = models.BooleanField(default=False)
    hypertention = models.BooleanField(default=False)

    ankle_edema = models.BooleanField(default=False)
    rheumatic_fever = models.BooleanField(default=False)
    rheumatic_fever_age = models.CharField(max_length=3, blank=True, null=True)
    stroke_history = models.BooleanField(default=False)
    stroke_date = models.DateField(
        default=now, blank=True, null=True)

    def __str__(self):
        return super().__str__()


class ArthritisHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_arthritis')
    joint_pain = models.BooleanField(default=False)
    joint_swelling = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class NervousHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_nervous')
    headaches = models.BooleanField(default=False)
    convulsions_or_epilepsy = models.BooleanField(default=False)
    numbness_or_tingles = models.BooleanField(default=False)
    dizziness_or_fainting = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class LiverHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_liver')
    jaundice = models.BooleanField(default=False)
    history_of_liver_disease = models.BooleanField(default=False)
    specifics = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return super().__str__()


class WomenHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_women')
    pregnancy = models.BooleanField(default=False)
    pregnancy_month = models.CharField(max_length=2, blank=True, null=True)
    breast_feed = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class RespitoryHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_respiratory')
    persistant_cough = models.BooleanField(default=False)
    breathing_difficulty = models.BooleanField(default=False)
    shortness_of_breath = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class EarHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_ear')
    hearing_loss = models.BooleanField(default=False)
    ringing_of_ears = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class BloodHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_blood')
    bruise_easy = models.BooleanField(default=False)
    anemia = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class ThyroidHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_thyroid')
    perspire_easy = models.BooleanField(default=False)
    apprehension = models.BooleanField(default=False)
    palpitation = models.BooleanField(default=False)
    goiter = models.BooleanField(default=False)
    bulging_eyes = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class DiabetesHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_diabetes')
    delayed_healing = models.BooleanField(default=False)
    increased_appetite = models.BooleanField(default=False)
    family_history = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class RadiographyHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_radiography')
    radiography_therapy = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class UrinaryHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_urinary')
    increased_frequency = models.BooleanField(default=False)
    burning = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


class HospitalizationHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_hospitalization')
    hospitalized = models.BooleanField(default=False)
    admission_date = models.DateField(
        default=now, blank=True, null=True)
    specifics = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return super().__str__()


class AllergiesHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_allergies')
    sleeping_pills = models.BooleanField(default=False)
    aspirin = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    penicilin = models.BooleanField(default=False)
    antibiotics = models.BooleanField(default=False)
    sulfa_drugs = models.BooleanField(default=False)
    local_anesthesia = models.BooleanField(default=False)
    others = models.BooleanField(default=False)
    specifics = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return super().__str__()


class ExtractionHistory(models.Model):
    history = models.OneToOneField(
        MedicalHistory, on_delete=models.CASCADE, related_name='history_extraction')
    prev_extraction = models.BooleanField(default=False)
    date_of_last_extraction = models.DateField(
        now, blank=True, null=True)
    untoward_reaction = models.BooleanField(default=False)
    specifics = models.TextField(max_length=500, blank=True, null=True)
    local_anesthesia_use = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()
