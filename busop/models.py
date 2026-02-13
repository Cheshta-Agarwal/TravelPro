from django.db import models

# Create your models here.

class busop_user(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=18)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    OTP = models.CharField(max_length=6)

    def __str__(self):
        return self.username
    
    
class Bus(models.Model):
    bus_number = models.CharField(max_length=20)
    route = models.CharField(max_length=100)
    bus_type = models.CharField(max_length=20) #e.g., AC, non-AC
    capacity = models.IntegerField(default=60)
    driver_name = models.CharField(max_length=50)

    def __str__(self):
        return self.bus_number

class Route(models.Model):
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    distance = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.source} to {self.destination}"
    
class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.bus.bus_number} - {self.route} at {self.departure_time}"
    
class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bus.bus_number} - Seat {self.seat_number}"
    
    