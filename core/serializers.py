from rest_framework import serializers
from .models import *
from users.models import User


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'contact', 'address', 'gender', 'blood_group', 'age', 'email', 'telephone', 'occupation', 'nationality', 'marital_status',
            'reffered_by', 'emergency_contact_name', 'emergency_contact_contact',
            'emergency_contact_address', 'emergency_contact_relation', 'date_created'
        ]
