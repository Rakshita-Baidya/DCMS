from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Patient)
admin.site.register(MedicalHistory)
admin.site.register(OtherPatientHistory)

admin.site.register(DentalChart)
admin.site.register(ToothRecord)

admin.site.register(Appointment)

admin.site.register(TreatmentPlan)
admin.site.register(TreatmentRecord)
admin.site.register(TreatmentDoctor)

admin.site.register(PurchasedProduct)

admin.site.register(Transaction)
