from django.urls import path
from . import views
from .views import RegisterView, ApproveRequestView


urlpatterns = [
    # backend urls
    path('register/', RegisterView.as_view(), name='register'),
    path('approve/<int:pk>/', ApproveRequestView.as_view(), name='approve-request'),

]
