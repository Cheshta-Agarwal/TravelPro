from django.urls import path
from . import views
from busop import views as busop_views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("profile", views.profile, name="profile"),
    path("otp_login",views.otp_login_view,name="otp_login"),
    path("otp_verify",views.otp_verify_view,name="otp_verify"),
    path("booking_history",busop_views.booking_history,name="booking_history"),
    path("create_booking/<int:schedule_id>/",busop_views.create_booking,name="create_booking"),
]
