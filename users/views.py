# from django.shortcuts import render, redirect, get_object_or_404


# from rest_framework import generics, status
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from .models import User, RegistrationRequest
# from .serializers import RegistrationRequestSerializer, ApproveRequestSerializer

# # Create your views here.


# class register_view(generics.CreateAPIView):
#     queryset = RegistrationRequest.objects.all()
#     serializer_class = RegistrationRequestSerializer
#     permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         user = serializer.save()
#         RegistrationRequest.objects.create(user=user, status='Pending')

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         return Response({'message': 'Registration submitted!'})

# # Approve or Deny User


# class ApproveRequestView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):
#         try:
#             reg_request = RegistrationRequest.objects.get(pk=pk)
#             action = request.data.get('action')

#             if action == 'approve':
#                 reg_request.status = 'Approved'

#                 role = request.data.get('role')
#                 reg_request.user.role = role

#                 reg_request.user.is_active = True
#                 reg_request.user.save()

#             elif action == 'deny':
#                 reg_request.status = 'Denied'

#             reg_request.save()
#             return Response({'message': f'Request {action}d!'})

#         except RegistrationRequest.DoesNotExist:
#             return Response({'error': 'Request not found.'})


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from .models import User
from django.contrib.auth.decorators import login_required


def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User must be approved first
            user.save()
            messages.success(
                request, "Registration successful. Wait for approval.")
            return redirect('login')
        else:
            messages.error(
                request, "There was an error with your registration.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Login successful!")
                    # Update to your redirect path
                    return redirect('list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def list_users(request):
    # Allow only superusers and admins
    if not request.user.is_superuser and request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('login')

    # Fetch all users
    all_users = User.objects.all()

    return render(request, 'all_users.html', {'users': all_users})

# Approval View


@login_required
def approve_users(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('login')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        action = request.POST.get('action')

        try:

            user = User.objects.get(id=user_id)
            if action == 'approve':
                if user and not user.is_superuser:
                    user.is_active = True
                    user.role = role
                    user.save()
                    messages.success(
                        request, f"{user.username} approved successfully.")
                else:
                    messages.error(
                        request, "Invalid user or cannot approve superuser.")

            elif action == 'deny':
                if user and not user.is_superuser:
                    user.delete()
                    messages.success(
                        request, f"{user.username} denied and removed successfully.")
                else:
                    messages.error(
                        request, "Invalid user or cannot remove superuser.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    # Fetch pending users (those with is_active=False)
    pending_users = User.objects.filter(is_active=False)

    return render(request, 'approve_users.html', {'users': pending_users})
