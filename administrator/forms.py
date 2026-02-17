from django import forms
from django.apps import apps


class BusForm(forms.ModelForm):
    class Meta:
        Bus = apps.get_model('busop', 'Bus')
        model = Bus
        fields = ['bus_number', 'route', 'bus_type', 'capacity', 'driver_name']


class RouteForm(forms.ModelForm):
    class Meta:
        Route = apps.get_model('busop', 'Route')
        model = Route
        fields = ['source', 'destination', 'distance']
