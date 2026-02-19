from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("profile", views.profile, name="profile"),
    path("otp_login",views.otp_login_view,name="otp_login"),
    path("otp_verify",views.otp_verify_view,name="otp_verify")
]
