from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils import timezone
from busop.models import Schedule
# Create your views here.
from .models import Booking, Payment


def create_booking(request):
    
    #Handles secure seat reservation and payment processing.

    if request.method == 'POST':
        # 1. Extract data from POST
        passenger_name = request.POST.get('passenger_name')
        passenger_email = request.POST.get('passenger_email')
        passenger_phone = request.POST.get('passenger_phone')
        schedule_id = request.POST.get('schedule_id')
        seat_id = request.POST.get('seat_id')

        try:
            # Core Logic: Use atomic transactions to satisfy Section 46 [cite: 46]
            with transaction.atomic():
                # select_for_update() locks rows to prevent double-booking
                if Booking.objects.select_for_update().filter(schedule_id=schedule_id, seat_id=seat_id).exists():
                    return render(request, 'booking_error.html', {'error': 'This seat was just taken. Please choose another.'})

                # Fetch the schedule to get the current price
                schedule = get_object_or_404(Schedule, id=schedule_id)

                # 3. Create the Booking record
                booking = Booking.objects.create(
                    user=request.user,
                    schedule=schedule,
                    seat_id=seat_id,
                    status='Confirmed'
                )

                # 4. Process Payment Integration [cite: 38]
                Payment.objects.create(
                    booking=booking,
                    amount=schedule.price,
                    transaction_id=f"TPRO-{timezone.now().strftime('%y%m%d')}-{booking.id}",
                    payment_status='Success'
                )

            # Success response
            return render(request, 'booking_success.html', {'booking': booking})

        except Exception as e:
            return render(request, 'booking_error.html', {'error': f"Transaction failed: {str(e)}"})

    else:
        # GET request logic: Fetch schedule and available seats for the UI
        schedule_id = request.GET.get('schedule_id')
        if not schedule_id:
            return redirect('bus_search') # Redirect if user didn't select a bus [cite: 29]

        schedule = get_object_or_404(Schedule, id=schedule_id)
        
        available_seats = schedule.get_available_seats()

        context = {
            'schedule': schedule,
            'available_seats': available_seats
        }
        return render(request, 'create_booking.html', context)
    
def process_booking_logic(request, schedule, seat):
    try:
        with transaction.atomic():
            #select_for_update() locks the rows in the database until the transaction is complete, preventing other transactions from modifying them and thus avoiding double-booking.
            if Booking.objects.select_for_update().filter(schedule=schedule, seat=seat).exists():
                return False, 'Seat already booked'
            
            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                seat=seat,
                passenger_name=request.POST.get('passenger_name'),
                passenger_email=request.POST.get('passenger_email'),
                passenger_phone=request.POST.get('passenger_phone')
            )

            payment=Payment.objects.create(
                booking=booking,
                amount=schedule.price,
                transaction_id=f"TXN-{booking.id}-{request.user.id}",
                payment_status='Success'
            )

            return True, booking
    except Exception as e:
        return False, str(e)
    
def booking_history(request):

    bookings=Booking.objects.filter(user=request.user).select_related(
        'schedule__bus', 'schedule__route', 'seat'
        ).order_by('-booking_date')
    
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

