from django.shortcuts import render, redirect
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages as django_messages
from django.utils import timezone
from busop.models import Schedule,Seat
from django.contrib.auth.decorators import login_required
# Create your views here.
from user.models import Booking, Payment
from django.contrib.auth import authenticate, login, logout
# Create your views here.

from busop.models import Schedule

def admin_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_staff: # The logic check must happen here
            login(request, user)
            return redirect('administrator:dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid credentials or not staff'})
    return render(request, 'admin_login.html')

def admin_login_page(request):
    return render(request, 'admin_login.html')

def admin_logout(request):
    """
    Core Logic: Securely flushes the admin session.
    Redirects to the admin login page with a success message.
    """
    logout(request)
    django_messages.success(request, "You have been logged out successfully.")
    return redirect('admin_login')

def bus_search(request):
    # 1. Initialize variables at the top to avoid UnboundLocalError
    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')
    schedules = []

    # 2. Perform the logic only if we have search parameters
    if source and destination:
        # Optimized with select_related to meet the < 3s requirement
        schedules = Schedule.objects.select_related('bus', 'route').filter(
            route__source__icontains=source,
            route__destination__icontains=destination
        )
        
        if departure_date:
            schedules = schedules.filter(departure_time__date=departure_date)

        # Core Logic: Calculate availability for each schedule
        for schedule in schedules:
            # 1. Get total seats automated by your signal
            total_seats = Seat.objects.filter(bus=schedule.bus).count()
            
            # 2. Count current confirmed bookings
            booked_count = Booking.objects.filter(
                schedule=schedule, 
                status='Confirmed'
            ).count()
            
            # 3. Attach the math to the object for the template
            schedule.available_seats = total_seats - booked_count
            
            # 4. Determine status for the UI
            schedule.is_sold_out = schedule.available_seats <= 0

    context = {
        'schedules': schedules,
        'source': source,
        'destination': destination,
        'departure_date': departure_date
    }

    return render(request, 'busop_search.html', context)

@login_required
def create_booking(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    # Core Logic: Fetch only available seats for this specific bus
    available_seats = Seat.objects.filter(bus=schedule.bus, is_available=True)

    if request.method == 'POST':
        seat_id = request.POST.get('seat')
        passenger_name = request.POST.get('passenger_name')
        passenger_email = request.POST.get('passenger_email')
        passenger_phone = request.POST.get('passenger_phone')

        # Member 3: Using a transaction to ensure data integrity
        with transaction.atomic():
            selected_seat = get_object_or_404(Seat, id=seat_id, is_available=True)
            
            # 1. Create the booking record
            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                seat=selected_seat,
                passenger_name=passenger_name,
                passenger_email=passenger_email,
                passenger_phone=passenger_phone,
                status='Confirmed'
            )
            
            # 2. Mark the seat as no longer available
            selected_seat.is_available = False
            selected_seat.save()

            return redirect('booking_history')

    return render(request, 'create_booking.html', {
        'schedule': schedule,
        'available_seats': available_seats
    })

def booking_history(request):

    bookings=Booking.objects.filter(user=request.user).select_related(
        'schedule__bus', 'schedule__route', 'seat'
        ).order_by('-id')
    
    return render(request, 'booking_history.html', {'bookings': bookings})

def cancel_booking(request, booking_id):
    # Ensure the user can only cancel their own booking
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # 1. Check time constraint: Cannot cancel within 1 hour of departure
    if booking.schedule.departure_time - timezone.now() < timezone.timedelta(hours=1):
        return render(request, 'cancel_error.html', {
            'error': 'Cancellations are not allowed within 1 hour of departure.'
        })

    # 2. Update Booking and associated records
    if booking.status != 'Cancelled':
        booking.status = 'Cancelled'
        booking.save()

        # Update seat availability so others can book it
        seat = booking.seat
        seat.is_available = True
        seat.save()

        # Update payment status using your specific model field
        Payment.objects.filter(booking=booking).update(payment_status='Refunded')

        django_messages.success(request, f"Booking #{booking.id} has been cancelled. Your seat {seat.seat_number} is now released.")

    return redirect('booking_history')

def generate_invoice(request, booking_id):
    # Ensure the booking belongs to the logged-in user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Try to get payment info, but don't crash if it's missing
    payment = Payment.objects.filter(booking=booking).first()

    context = {
        'booking': booking,
        'payment': payment, # This will be None if no payment exists
        'bus': booking.schedule.bus,
        'route': booking.schedule.route,
        'schedule': booking.schedule,
        'seat': booking.seat,
    }
    return render(request, 'invoice.html', context)
