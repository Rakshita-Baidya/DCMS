from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, StaffForm, DoctorForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


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
                # Check if the user has already completed their first login setup
                if user.last_login is None:
                    # Store user ID temporarily in session
                    request.session['temp_user_id'] = user.id

                    # Redirect based on role to the corresponding form
                    if user.role == 'staff':
                        return redirect('staff_form')
                    elif user.role == 'doctor':
                        return redirect('doctor_form')
                    elif user.role == 'admin':
                        login(request, user)  # Directly log in admins
                        return redirect('core:dashboard')
                else:
                    # Directly log the user in if it's not their first login
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect('core:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def staff_form(request):
    temp_user_id = request.session.get('temp_user_id')

    # Ensure temp_user_id exists in session
    if not temp_user_id:
        messages.error(request, "No user session found. Please log in again.")
        return redirect('login')

    temp_user = User.objects.get(id=temp_user_id)

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff_profile = form.save(commit=False)
            staff_profile.user = temp_user
            staff_profile.save()

            # Log the user in after completing the form
            login(request, temp_user)
            del request.session['temp_user_id']  # Clear session
            messages.success(request, "Welcome! Your details have been saved.")
            return redirect('core:dashboard')
    else:
        form = StaffForm()

    return render(request, 'staff_form.html', {'form': form})


def doctor_form(request):
    temp_user_id = request.session.get('temp_user_id')

    # Ensure temp_user_id exists in session
    if not temp_user_id:
        messages.error(request, "No user session found. Please log in again.")
        return redirect('login')

    temp_user = User.objects.get(id=temp_user_id)

    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor_profile = form.save(commit=False)
            doctor_profile.user = temp_user
            doctor_profile.save()

            # Log the user in after completing the form
            login(request, temp_user)
            del request.session['temp_user_id']  # Clear session
            messages.success(request, "Welcome! Your details have been saved.")
            return redirect('core:dashboard')
    else:
        form = DoctorForm()

    return render(request, 'doctor_form.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def list_users(request):

    # Allow only superusers and admins
    if not request.user.is_superuser and request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('login')
    else:
        user_queryset = User.objects.all()

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

    return render(request, 'all_users.html', context)

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
                    user.is_approved = "Approved"
                    user.role = role
                    user.save()
                    messages.success(
                        request, f"{user.username} approved successfully.")
                else:
                    messages.error(
                        request, "Invalid user.")

            elif action == 'deny':
                if user and not user.is_superuser:
                    user.is_active = False
                    user.is_approved = "Denied"
                    user.save()
                    messages.success(
                        request, f"{user.username} denied successfully.")
                else:
                    messages.error(
                        request, "Invalid user.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    # Fetch pending users
    user_queryset = User.objects.filter(is_approved="Pending")

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        user_queryset = user_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
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

    return render(request, 'approve_users.html', context)
