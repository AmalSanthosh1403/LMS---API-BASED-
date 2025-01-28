from django.urls import path
from .import views

urlpatterns = [
    path('user/create/', views.create_user, name='create_user'),
    path('user/', views.user_management, name='list_users'),  # List all users, single function for both functionality    
]
