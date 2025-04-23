from django.contrib import admin
from .models import Patient, MedicalHistory, DentalChart, ToothRecord, Appointment, TreatmentPlan, TreatmentRecord, TreatmentDoctor, PurchasedProduct, Transaction, Payment

# Register your models here.


admin.site.register(Patient)
admin.site.register(MedicalHistory)
admin.site.register(TreatmentPlan)

admin.site.register(DentalChart)
admin.site.register(ToothRecord)

admin.site.register(Appointment)

admin.site.register(TreatmentRecord)
admin.site.register(TreatmentDoctor)
admin.site.register(PurchasedProduct)
admin.site.register(Payment)

admin.site.register(Transaction)
