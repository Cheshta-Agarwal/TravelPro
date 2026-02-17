from django.contrib import admin

# Register your models here.
from .models import Booking, Payment, transaction, user
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(user)
admin.site.register(transaction)    



