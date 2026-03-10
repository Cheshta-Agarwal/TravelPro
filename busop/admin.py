from django.contrib import admin

# Register your models here.
from .models import Bus, Route, Schedule, Seat, busop_user
admin.site.register(Bus)
#admin.site.register(Route)  
admin.site.register(Schedule)
admin.site.register(Seat)
admin.site.register(busop_user)

from django.contrib import admin
from .models import Route, Stop

# This allows stops to be edited on the same page as the Route
class StopInline(admin.TabularInline):
    model = Stop
    extra = 3 # Shows 3 empty rows by default

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination')
    inlines = [StopInline]

