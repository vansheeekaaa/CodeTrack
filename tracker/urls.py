from django.urls import path, include
from . import views  # Import views from the same app

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    # For social authentication (Google login)
    path("accounts/", include("allauth.urls")),
    path("dashboard/", views.dashboard, name="dashboard"),
]
