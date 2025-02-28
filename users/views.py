from rest_framework_simplejwt.tokens import RefreshToken
from .forms import LoginForm
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import Group
from .forms import UserCreationForm, LoginForm, UserEditForm
from .models import User
from .serializers import UserSerializer
from .decorators import admin_only, allowed_users, unauthenticated_user


# def user_register(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # User must be approved first
#             user.save()
#             messages.success(
#                 request, "Registration successful. Wait for approval.")
#             return redirect('login')
#         else:
#             messages.error(
#                 request, "There was an error with your registration.")
#     else:
#         form = UserForm()
#     return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)

                # Store tokens
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Set the JWT as an HTTP-only cookie
                response = redirect('core:dashboard')
                response.set_cookie(
                    key='jwt',
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax'
                )
                response['Authorization'] = f'Bearer {access_token}'

                messages.success(request, "Login successful!")
                return response
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@allowed_users(allowed_roles=['Administrator'])
def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            role = form.cleaned_data.get('role')
            if role == 'Staff':
                group = Group.objects.get(name='Staff')
            elif role == 'Doctor':
                group = Group.objects.get(name='Doctor')
            elif role == 'Administrator':
                group = Group.objects.get(name='Administrator')
            else:
                group = None

            if group:
                user.groups.add(group)

            messages.success(
                request, 'User created successfully.')
            return redirect('list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'form': form,
        'title': 'Add New User'
    }
    return render(request, 'add_user.html', context)


@login_required
def user_logout(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('jwt')
    return response


@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrator'])
def users_list(request):

    # Allow only superusers and admins
    # if not request.user.is_superuser and request.user.role != 'Administrator':
    #     messages.error(request, "Access denied.")
    #     return redirect('login')
    # else:
    user_queryset = User.objects.all().order_by('role')

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        user_id_to_delete = request.POST['delete_user_id']
        user_to_delete = User.objects.get(id=user_id_to_delete)
        user_to_delete.delete()
        messages.success(request, f"User {
                         user_to_delete.username} has been deleted.")

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        user_queryset = user_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(user_queryset, 8)
    page = request.GET.get('page', 1)
    user_list = paginator.get_page(page)

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'users': user_list,
        'total_user': user_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'reg_users/users_list.html', context)

# Approval View


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['Administrator'])
# def user_approve(request):
#     # if not request.user.is_superuser and request.user.role != 'Administrator':
#     #     messages.error(request, "Access denied.")
#     #     return redirect('login')

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         role = request.POST.get('role')
#         action = request.POST.get('action')

#         try:
#             user = User.objects.get(id=user_id)
#             if action == 'approve':
#                 if user and not user.is_superuser:
#                     user.is_active = True
#                     user.is_approved = "Approved"
#                     user.role = role
#                     user.save()

#                     group, created = Group.objects.get_or_create(name=role)
#                     user.groups.add(group)

#                     messages.success(
#                         request, f"{user.username} approved successfully.")
#                 else:
#                     messages.error(
#                         request, "Invalid user.")

#             elif action == 'deny':
#                 if user and not user.is_superuser:
#                     user.is_active = False
#                     user.is_approved = "Denied"
#                     user.save()
#                     messages.success(
#                         request, f"{user.username} denied successfully.")
#                 else:
#                     messages.error(
#                         request, "Invalid user.")

#         except User.DoesNotExist:
#             messages.error(request, "User not found.")

#     # Fetch pending users
#     user_queryset = User.objects.filter(is_approved="Pending").order_by('id')

#     # Add search functionality
#     search_query = request.GET.get('search', '')
#     if search_query:
#         user_queryset = user_queryset.filter(
#             Q(first_name__icontains=search_query) |
#             Q(last_name__icontains=search_query)
#         )

#     # Pagination
#     paginator = Paginator(user_queryset, 8)
#     page = request.GET.get('page', 1)
#     user_list = paginator.get_page(page)

#     context = {
#         'page_title': 'User Management',
#         'active_page': 'users',
#         'users': user_list,
#         'total_user': user_queryset.count(),
#         'search_query': search_query,
#     }

#     return render(request, 'reg_users/user_approve.html', context)


@login_required(login_url='login')
def user_profile(request):
    user_queryset = User.objects.get(pk=request.user.id)

    # # Initialize profile data
    # staff_profile = None
    # doctor_profile = None

    # # Check the user's role and fetch data accordingly
    # if user_queryset.role == 'Staff':
    #     staff_profile = user_queryset
    # elif user_queryset.role == 'Doctor':
    #     doctor_profile = user_queryset

    # Pass the profile data to the context
    context = {
        'page_title': 'User Profile',
        'user': user_queryset,
        # 'staff_profile': staff_profile,
        # 'doctor_profile': doctor_profile,
    }

    return render(request, 'profile/profile.html', context)


@login_required(login_url='login')
def edit_profile(request):
    user_queryset = User.objects.get(pk=request.user.id)
    # staff_profile = None
    # doctor_profile = None

    # # Fetch profile data based on the user's role
    # if user_queryset.role == 'Staff':
    #     staff_profile = user_queryset.staff_profile
    # elif user_queryset.role == 'Doctor':
    #     doctor_profile = user_queryset.doctor_profile

    # if request.method == 'POST':
    #     user_form = UserEditForm(
    #         request.POST, request.FILES, instance=user_queryset)
    #     staff_form = StaffForm(
    #         request.POST, instance=staff_profile) if staff_profile else None
    #     doctor_form = DoctorForm(
    #         request.POST, instance=doctor_profile) if doctor_profile else None

    #     if user_form.is_valid():
    #         user_form.save()
    #         if staff_form and staff_form.is_valid():
    #             staff_form.save()
    #         if doctor_form and doctor_form.is_valid():
    #             doctor_form.save()

    #         messages.success(
    #             request, 'The profile has been updated successfully!')
    #         return redirect('profile')
    # else:
    #     user_form = UserEditForm(instance=user_queryset)
    #     staff_form = StaffForm(
    #         instance=staff_profile) if staff_profile else None
    #     doctor_form = DoctorForm(
    #         instance=doctor_profile) if doctor_profile else None

    context = {
        # 'user_form': user_form,
        # 'staff_form': staff_form,
        # 'doctor_form': doctor_form,
        'page_title': 'User Profile',
    }

    return render(request, 'profile/edit_profile.html', context)


@login_required(login_url='login')
def view_user_profile(request, user_id):
    user_queryset = User.objects.get(pk=user_id)
    staff_profile = None
    doctor_profile = None

    # Fetch profile data based on the user's role
    if user_queryset.role == 'Staff' and hasattr(user_queryset, 'staff_profile'):
        staff_profile = user_queryset.staff_profile
    elif user_queryset.role == 'Doctor' and hasattr(user_queryset, 'doctor_profile'):
        doctor_profile = user_queryset.doctor_profile

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        if not request.user.is_superuser and request.user.role != 'Administrator':
            messages.error(request, "You do not have permission to delete.")
        else:
            user_id_to_delete = request.POST['delete_user_id']
            user_to_delete = User.objects.get(id=user_id_to_delete)
            user_to_delete.delete()
            messages.success(request, f"User {
                user_to_delete.username} has been deleted.")
            return redirect('view_user_profile')

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'user': user_queryset,
        'staff_profile': staff_profile,
        'doctor_profile': doctor_profile,
    }

    return render(request, 'reg_users/view_user_profile.html', context)


@login_required(login_url='login')
def edit_user_profile(request, user_id):
    # user_queryset = User.objects.get(pk=user_id)
    # staff_profile = None
    # doctor_profile = None

    # # Fetch profile data based on the user's role
    # if user_queryset.role == 'Staff' and hasattr(user_queryset, 'staff_profile'):
    #     staff_profile = user_queryset.staff_profile
    # elif user_queryset.role == 'Doctor' and hasattr(user_queryset, 'doctor_profile'):
    #     doctor_profile = user_queryset.doctor_profile

    # # user needs to be deleted
    # if request.method == 'POST' and 'delete_user_id' in request.POST:
    #     if not request.user.is_superuser and request.user.role != 'Administrator':
    #         messages.error(request, "You do not have permission to delete.")
    #     else:
    #         user_id_to_delete = request.POST['delete_user_id']
    #         user_to_delete = User.objects.get(id=user_id_to_delete)
    #         user_to_delete.delete()
    #         messages.success(request, f"User {
    #             user_to_delete.username} has been deleted.")
    #         return redirect('list')

    # if request.method == 'POST':
    #     user_form = UserEditForm(
    #         request.POST, request.FILES, instance=user_queryset)
    #     staff_form = StaffForm(
    #         request.POST, instance=staff_profile) if staff_profile else None
    #     doctor_form = DoctorForm(
    #         request.POST, instance=doctor_profile) if doctor_profile else None

    #     if user_form.is_valid():
    #         user_form.save()
    #         if staff_form and staff_form.is_valid():
    #             staff_form.save()
    #         if doctor_form and doctor_form.is_valid():
    #             doctor_form.save()

    #         messages.success(
    #             request, 'Your profile has been updated successfully!')
    #         return redirect('view_user_profile', user_id=user_queryset.id)
    # else:
    #     user_form = UserEditForm(instance=user_queryset)
    #     staff_form = StaffForm(
    #         instance=staff_profile) if staff_profile else None
    #     doctor_form = DoctorForm(
    #         instance=doctor_profile) if doctor_profile else None

    context = {
        # 'user': user_queryset,
        # 'user_form': user_form,
        # 'staff_form': staff_form,
        # 'doctor_form': doctor_form,
        'page_title': 'User Management',
        'active_page': 'users',
    }

    return render(request, 'reg_users/edit_user_profile.html', context)
