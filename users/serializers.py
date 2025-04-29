from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['date_joined', 'last_login',
                            'is_superuser', 'is_staff', 'is_active']
