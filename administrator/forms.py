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

from busop.models import Schedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['bus', 'route', 'departure_time', 'arrival_time', 'price']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

from django.forms import inlineformset_factory
from busop.models import Route, Stop

# This creates a formset to add multiple stops to a single route
StopFormSet = inlineformset_factory(
    Route, Stop, 
    fields=['location_name', 'stop_order'], 
    extra=3, 
    can_delete=True
)