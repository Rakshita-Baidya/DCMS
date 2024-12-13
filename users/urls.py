from django.urls import path
from . import views
from .views import user_login, user_logout, user_register, approve_users


urlpatterns = [
    # backend urls
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('approve/', approve_users, name='approve_users'),
]
