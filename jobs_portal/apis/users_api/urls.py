from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterUser.as_view(), name="register_user"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfile.as_view(), name="user_profile"),
]
