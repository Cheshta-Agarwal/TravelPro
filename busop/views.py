from django.shortcuts import render
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.utils import timezone
from busop.models import Schedule
# Create your views here.
from user.models import Booking, Payment

# Create your views here.

from busop.models import Schedule


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

<<<<<<< HEAD
        

    # 3. Define the context OUTSIDE the if blocks
=======
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

>>>>>>> origin/feature/corelogic
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

    return render(request, 'user/create_booking.html', {
        'schedule': schedule,
        'available_seats': available_seats
    })

def booking_history(request):

    bookings=Booking.objects.filter(user=request.user).select_related(
        'schedule__bus', 'schedule__route', 'seat'
        ).order_by('-id')
    
    return render(request, 'booking_history.html', {'bookings': bookings})

def cancel_booking(request,booking_id):
    booking=get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.schedule.departure_time - timezone.now() < timezone.timedelta(hours=1):
        return render(request, 'cancel_error.html', {'error': 'Cannot cancel bookings less than 1 hour before departure.'})

    if booking.status == 'Confirmed':
        booking.status = 'Cancelled'
        booking.save()

        # Update payment status to 'Refunded' 
        Payment.objects.filter(booking=booking).update(payment_status='Refunded')

        messages.success(request, f"Booking #{booking.id} has been cancelled successfully.")

    return redirect('booking_history')  # Redirect to booking history page after cancellation

def generate_invoice(request, booking_id):
    booking=get_object_or_404(Booking, id=booking_id, user=request.user)
    payment=get_object_or_404(Payment, booking=booking)

    context={
        'booking': booking,
        'payment': payment,
        'bus':booking.schedule.bus,
        'route':booking.schedule.route,
        'schedule':booking.schedule,
        'seat':booking.seat,
    }
    return render(request, 'invoice.html', context)

