from django.shortcuts import render, redirect
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages as django_messages
from django.utils import timezone
from busop.models import Schedule,Seat,Stop
from django.contrib.auth.decorators import login_required
from decimal import Decimal
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
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')

    # Start with all schedules
    schedules = Schedule.objects.all()

    if source and destination:
        # Member 3: Added prefetch_related('route__stops') to optimize database hits
        schedules = schedules.filter(
            route__source__icontains=source,
            route__destination__icontains=destination
        ).select_related('bus', 'route').prefetch_related('route__stops')

    if departure_date:
        schedules = schedules.filter(departure_time__date=departure_date)

    return render(request, 'busop_search.html', {
        'schedules': schedules,
        'source': source,
        'destination': destination,
        'departure_date': departure_date
    })

@login_required
def create_booking(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    route_stops = schedule.route.stops.all().order_by('stop_order')
    available_seats = Seat.objects.filter(bus=schedule.bus, is_available=True)

    # Member 3: Define Tiered Discounts
    discount_map = {
        1: Decimal('0.60'), # 40% off
        2: Decimal('0.75'), # 25% off
    }
    default_discount = Decimal('0.90') # 10% off for any other stop

    if request.method == 'POST':
        seat_id = request.POST.get('seat')
        stop_id = request.POST.get('drop_off_point')
        passenger_name = request.POST.get('passenger_name')
        
        final_fare = schedule.price 
        selected_stop = None

        if stop_id:
            selected_stop = get_object_or_404(Stop, id=stop_id)
            # Use the tiered map logic
            factor = discount_map.get(selected_stop.stop_order, default_discount)
            final_fare = (schedule.price * factor).quantize(Decimal('1.00'))

        with transaction.atomic():
            selected_seat = get_object_or_404(Seat, id=seat_id, is_available=True)

            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                seat=selected_seat,
                drop_off_point=selected_stop, 
                passenger_name=passenger_name,
                status='Confirmed'
            )
            
            selected_seat.is_available = False
            selected_seat.save()

            Payment.objects.create(
                booking=booking,
                amount=final_fare, 
                payment_method='Direct/On-Board',
                payment_status='completed'
            )

            return redirect('booking_history')

    # Prepare stops with their specific prices for the dropdown
    stops_with_prices = []
    for stop in route_stops:
        factor = discount_map.get(stop.stop_order, default_discount)
        price = (schedule.price * factor).quantize(Decimal('1.00'))
        stops_with_prices.append({
            'id': stop.id,
            'name': stop.location_name,
            'price': price
        })

    return render(request, 'create_booking.html', {
        'schedule': schedule,
        'available_seats': available_seats,
        'stops_with_prices': stops_with_prices
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
