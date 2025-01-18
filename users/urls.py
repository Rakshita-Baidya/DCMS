from django.urls import path
from . import views
from .views import user_login, user_logout, user_register, list_users, approve_users, staff_form, doctor_form
from django.contrib.auth import views as auth_views

# app_name = 'users'

urlpatterns = [
    # backend urls
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('staff_form/', staff_form, name='staff_form'),
    path('doctor_form/', doctor_form, name='doctor_form'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_form.html'),
         name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'),
         name='password_reset_complete'),

    path('logout/', user_logout, name='logout'),


    path('list/', list_users, name='list'),
    path('approve/', approve_users, name='approve'),
]
