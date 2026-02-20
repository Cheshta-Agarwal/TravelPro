from django.urls import path
from . import views

urlpatterns = [
    # Bus search
    path('bus_search/', views.bus_search, name='bus_search'),

    # Booking flow
    path('create_booking/', views.create_booking, name='create_booking'),
    path('booking_history/', views.booking_history, name='booking_history'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Invoice
    path('invoice/<int:booking_id>/', views.generate_invoice, name='generate_invoice'),


path('admin_login_page/',views.admin_login_page,name='admin_login_page'),
path('admin_login/',views.admin_login,name='admin_login'),
path('admin_logout/', views.admin_logout, name='admin_logout'),
]
