from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import UserCreationForm, LoginForm, UserEditForm
from .models import User
from .serializers import UserSerializer
from .decorators import AdminOnly, AllowedUsers, UnauthenticatedUser

# function for user deletion


def delete_user(request, user_to_delete, redirect_url):
    if not request.user.is_superuser and 'Administrator' not in request.user.groups.values_list('name', flat=True):
        messages.error(request, "You do not have permission to delete.")
        return None
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
                login(request, user)
                refresh = RefreshToken.for_user(user)
                response = redirect('core:dashboard')
                response.set_cookie(
                    key='jwt',
                    value=str(refresh.access_token),
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


@login_required
def user_logout(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('jwt')
    return response


@login_required(login_url='login')
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

    # Add filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        user_queryset = user_queryset.filter(
            role__iexact=role_filter)
    roles = User.objects.all().values_list(
        'role', flat=True).distinct()

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
        'role_filter': role_filter,
        'roles': roles,
    }

    return render(request, 'reg_users/users_list.html', context)


@login_required(login_url='login')
def user_profile(request):
    user = request.user
    context = {
        'page_title': 'User Profile',
        'user': user
    }
    return render(request, 'profile/profile.html', context)


@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    form = UserEditForm(request.POST or None,
                        request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    context = {
        'page_title': 'User Profile',
        'user_form': form,
        'user': user,
    }
    return render(request, 'profile/edit_profile.html', context)


@login_required(login_url='login')
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


@login_required(login_url='login')
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
