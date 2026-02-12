from django.contrib import admin

# Register your models here.
from .models import Booking, Payment
admin.site.register(Booking)
admin.site.register(Payment)


