
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from datetime import datetime

from .forms import AdministratorEditForm, DoctorEditForm, StaffEditForm, UserCreationForm, LoginForm, UserEditForm
from .models import User
from .serializers import UserSerializer
from .decorators import AllowedUsers, UnauthenticatedUser, jwt_required

# function for user deletion


def delete_user(request, user_to_delete, redirect_url):
    if not request.user.is_superuser and request.user.role != 'Administrator':
        messages.error(request, "You do not have permission to delete.")
        return redirect(redirect_url)
    if user_to_delete.role == 'Administrator':
        messages.error(request, "You cannot delete an Administrator.")
        return redirect(redirect_url)

    user_to_delete.delete()
    messages.success(
        request, f"User {user_to_delete.username} has been deleted.")
    return redirect(redirect_url)


class UserListViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]


@UnauthenticatedUser
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                response = redirect('core:dashboard')
                response.set_cookie(
                    key='access_token',
                    value=str(refresh.access_token),
                    httponly=True,
                    secure=True,
                    samesite='Lax'
                )
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite='Lax'
                )
                messages.success(request, "Login successful!")
                return response
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@jwt_required(login_url='login')
def user_logout(request):
    # Extract tokens from cookies (already validated by jwt_required)
    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')

    # Blacklist access token
    token = AccessToken(access_token)
    outstanding_token, _ = OutstandingToken.objects.get_or_create(
        token=access_token,
        defaults={
            'user': request.user,
            'jti': token['jti'],
            'expires_at': make_aware(datetime.fromtimestamp(token['exp'])),
        }
    )
    BlacklistedToken.objects.get_or_create(token=outstanding_token)

    # Blacklist refresh token (if present)
    if refresh_token:
        token = RefreshToken(refresh_token)
        token.blacklist()

    # Delete cookies and redirect
    messages.success(request, 'Logged out successfully.')
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@jwt_required(login_url='login')
@AllowedUsers(allowed_roles=['Administrator'])
def add_user(request):
    form = UserCreationForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        role = form.cleaned_data.get('role')

        if role in ['Staff', 'Doctor', 'Administrator']:
            group = Group.objects.get(name=role)
            user.groups.add(group)
        messages.success(request, 'User created successfully.')
        return redirect('list')

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'form': form,
    }
    return render(request, 'add_user.html', context)


@jwt_required(login_url='login')
@AllowedUsers(allowed_roles=['Administrator'])
def users_list(request):
    user_queryset = User.objects.all().order_by('role')
    serializer = UserSerializer

    # user needs to be deleted
    if request.method == 'POST' and 'delete_user_id' in request.POST:
        user_to_delete = get_object_or_404(
            User, id=request.POST['delete_user_id'])
        result = delete_user(request, user_to_delete, 'list')
        if result:
            return result

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        user_queryset = user_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        user_queryset = user_queryset.filter(role__iexact=role_filter)

    # Pagination
    paginator = Paginator(user_queryset, 8)
    page = request.GET.get('page', 1)
    user_list = paginator.get_page(page)

    # Roles for filter dropdown
    roles = User.objects.values('role').distinct().order_by('role')

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'users': user_list,
        'total_user': user_queryset.count(),
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': [r['role'] for r in roles],
    }
    return render(request, 'reg_users/users_list.html', context)


@jwt_required(login_url='login')
def user_profile(request):
    user = request.user
    context = {
        'page_title': 'User Profile',
        'user': user
    }
    return render(request, 'profile/profile.html', context)


@jwt_required(login_url='login')
def edit_profile(request):
    user = request.user
    # Select form based on user role
    if user.role == 'Administrator':
        form_class = AdministratorEditForm
    elif user.role == 'Staff':
        form_class = StaffEditForm
    elif user.role == 'Doctor':
        form_class = DoctorEditForm
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('profile')

    # Instantiate form with POST data or None
    form = form_class(request.POST or None,
                      request.FILES or None, instance=user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'page_title': 'User Profile',
        'user_form': form,
        'user': user,
    }
    return render(request, 'profile/edit_profile.html', context)


@jwt_required(login_url='login')
def view_user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST' and 'delete_user_id' in request.POST:
        result = delete_user(request, user, 'list')
        if result:
            return result

    context = {
        'page_title': 'User Management',
        'active_page': 'users',
        'user': user,
    }
    return render(request, 'reg_users/view_user_profile.html', context)


@jwt_required(login_url='login')
def edit_user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST' and 'delete_user_id' in request.POST:
        result = delete_user(request, user, 'list')
        if result:
            return result

    form = UserEditForm(request.POST or None,
                        request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'The profile has been updated successfully!')
        return redirect('view_user_profile', user_id=user.id)

    context = {
        'user': user,
        'user_form': form,
        'page_title': 'User Management',
        'active_page': 'users',
    }
    return render(request, 'reg_users/edit_user_profile.html', context)
