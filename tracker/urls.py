from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('accounts/signup/', views.signup, name='signup'),  
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout route
    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    
    # Google OAuth
    path('accounts/', include('allauth.urls')),  # allauth handles social logins automatically
]
