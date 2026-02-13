from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from busop.models import Schedule, Seat

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"Booking for {self.passenger_name} on {self.schedule}"
    
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20) #e.g., card, UPI, net banking
    payment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.booking.passenger_name}"

class user(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=18)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    OTP = models.CharField(max_length=6)

    def __str__(self):
        return self.username.username

class transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_method = models.CharField(max_length=20) #e.g., card, UPI, net banking
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction of {self.amount} for {self.user.username}"