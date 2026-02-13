from django.shortcuts import render
from django.db import transaction

from busop.models import Schedule
# Create your views here.
from .models import Booking, Payment

def create_booking(request):
    if request.method == 'POST':
        # 1. Extract data from POST
        passenger_name = request.POST.get('passenger_name')
        schedule_id = request.POST.get('schedule_id')
        seat_id = request.POST.get('seat_id')
        passenger_email = request.POST.get('passenger_email')
        passenger_phone = request.POST.get('passenger_phone')

        try:
            with transaction.atomic():
                # 2. Prevent Double-Booking 
                # Use select_for_update() to lock these rows in the DB during the transaction
                if Booking.objects.select_for_update().filter(schedule_id=schedule_id, seat_id=seat_id).exists():
                    return render(request, 'booking_error.html', {'error': 'Seat already booked'})
                # 3. Create the Booking record 
                booking = Booking.objects.create(
                    user=request.user,
                    schedule_id=schedule_id,
                    seat_id=seat_id,
                    passenger_name=passenger_name,
                    passenger_email=passenger_email,
                    passenger_phone=passenger_phone
                )

                # 4. Process Payment 
                # In a real app, calculate the price from the Schedule model 
                schedule = Schedule.objects.get(id=schedule_id)
                Payment.objects.create(
                    booking=booking,
                    amount=schedule.price,  # Use the actual price from the schedule
                    transaction_id=f"TXN-{booking.id}-{request.user.id}", 
                    payment_status='Success'
                )
                # If transaction finishes successfully
            return render(request, 'booking_success.html', {'booking': booking})

        except Exception as e:
            # Handle unexpected database errors
            return render(request, 'booking_error.html', {'error': str(e)})

    # GET request: Show the booking form
    return render(request, 'create_booking.html')


