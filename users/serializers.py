from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'address', 'contact',
                  'role', 'profile_image', 'specialization', 'qualification', 'nmc_no', 'position']
