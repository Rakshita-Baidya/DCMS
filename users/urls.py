from django.urls import path
from . import views
from .views import add_user, edit_profile, edit_user_profile, user_login, user_logout, user_profile, users_list, view_user_profile
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewset, UserListViewset

# app_name = 'users'

urlpatterns = [

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # testing apis
    path('users/user_list', UserListViewset.as_view({'get': 'list',
         'put': 'update', 'delete': 'destroy', 'post': 'create'}), name='user_list'),
    path('users/user/<int:pk>/', UserViewset.as_view({'get': 'retrieve',
         'put': 'update', 'delete': 'destroy', 'post': 'create'}), name='user'),



    # backend urls
    path('login/', user_login, name='login'),
    #     path('register/', user_register, name='register'),
    path('add_user/', add_user, name='add_user'),

    #     path('staff_form/', staff_form, name='staff_form'),
    #     path('doctor_form/', doctor_form, name='doctor_form'),
    path('logout/', user_logout, name='logout'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password/password_reset.html',
                                                                 email_template_name='password/password_reset_email.html',
                                                                 subject_template_name='password/password_reset_subject.txt'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_sent.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='password/password_reset_form.html'),
         name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_complete'),

    path('list/', users_list, name='list'),
    #     path('approve/', user_approve, name='approve'),
    path('profile/', user_profile, name='profile'),  # logged in user profile
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', view_user_profile, name='view_user_profile'),
    path('profile/<int:user_id>/edit/',
         edit_user_profile, name='edit_user_profile'),

]
