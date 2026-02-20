from django.contrib import admin
from django.urls import path
from busop import views as busop_views

urlpatterns = [
path('bus_search/', busop_views.bus_search, name='bus_search'),
path('admin_login_page/',busop_views.admin_login_page,name='admin_login_page'),
path('admin_login/',busop_views.admin_login,name='admin_login'),
path('admin_logout/', busop_views.admin_logout, name='admin_logout'),
path('generate_invoice/<int:booking_id>/', busop_views.generate_invoice, name='generate_invoice'),
]