from django.contrib import admin

# Register your models here.
from .models import Bus, Route, Schedule
admin.site.register(Bus)
admin.site.register(Route)  
admin.site.register(Schedule)

