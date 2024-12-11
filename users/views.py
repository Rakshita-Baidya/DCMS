from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, RegistrationRequest
from .serializers import RegistrationRequestSerializer, ApproveRequestSerializer

# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = RegistrationRequest.objects.all()
    serializer_class = RegistrationRequestSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        RegistrationRequest.objects.create(user=user, status='Pending')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({'message': 'Registration submitted!'})

# Approve or Deny User


class ApproveRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            reg_request = RegistrationRequest.objects.get(pk=pk)
            action = request.data.get('action')

            if action == 'approve':
                reg_request.status = 'Approved'

                role = request.data.get('role')
                reg_request.user.role = role

                reg_request.user.is_active = True
                reg_request.user.save()

            elif action == 'deny':
                reg_request.status = 'Denied'

            reg_request.save()
            return Response({'message': f'Request {action}d!'})

        except RegistrationRequest.DoesNotExist:
            return Response({'error': 'Request not found.'})
