from django import forms
from django.apps import apps


class BusForm(forms.ModelForm):
    class Meta:
        Bus = apps.get_model('busop', 'Bus')
        model = Bus
        fields = ['bus_number', 'bus_type', 'capacity', 'driver_name']


class RouteForm(forms.ModelForm):
    class Meta:
        Route = apps.get_model('busop', 'Route')
        model = Route
        fields = ['source', 'destination', 'distance']

from django import forms
from busop.models import Schedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['bus', 'route', 'departure_time', 'arrival_time', 'price']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }