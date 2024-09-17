
from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register_user'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user-detail/', views.UserDetailView.as_view(), name='user-details'),


  
]