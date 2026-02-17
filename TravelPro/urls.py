"""
URL configuration for TravelPro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user import views as user_views
from busop import views as busop_views
from administrator import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_booking/', user_views.create_booking, name='create_booking'),
    path('busop_search/', admin_views.busop_search, name='busop_search' ),
    path('bus_search/', busop_views.bus_search, name='bus_search'),
    path('booking_history/', user_views.booking_history, name='booking_history'),
    path('cancel_booking/<int:booking_id>/', user_views.cancel_booking, name='cancel_booking'),
    path('invoice/<int:booking_id>/', user_views.generate_invoice, name='generate_invoice'),
]
