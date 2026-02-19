from django.contrib import admin
from django.urls import path
from busop import views as busop_views

urlpatterns = [
path('bus_search/', busop_views.bus_search, name='bus_search'),
]