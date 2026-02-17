from django.contrib import admin

# Register your models here.
from .models import Bus, Route, Schedule, Seat, busop_user
admin.site.register(Bus)
admin.site.register(Route)  
admin.site.register(Schedule)
admin.site.register(Seat)
admin.site.register(busop_user)
