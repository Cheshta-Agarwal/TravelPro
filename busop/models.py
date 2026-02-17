from django.db import models
from django.forms import ValidationError

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
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def clean(self):
        # Prevent arrival before departure logic
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time.")
        
    def get_available_seats(self):
        #Logic to filter out seats already associated with a confirmed booking.
        # This import stays inside the function to avoid circular import errors 
        from user.models import Booking 
        
        # 1. Get IDs of seats already booked for this specific schedule [cite: 52]
        booked_seat_ids = Booking.objects.filter(
            schedule=self, 
            status__in=['Confirmed', 'Pending']
        ).values_list('seat_id', flat=True)
        
        # 2. Return all seats belonging to this bus except the booked ones [cite: 51]
        return Seat.objects.filter(bus=self.bus).exclude(id__in=booked_seat_ids)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.route} at {self.departure_time}"    

class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('bus', 'seat_number')  # Ensure seat numbers are unique per bus

    def __str__(self):
        return f"{self.bus.bus_number} - Seat {self.seat_number}"
    
