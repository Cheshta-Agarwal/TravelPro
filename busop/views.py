from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from busop.models import Schedule, Seat
from user.models import Booking, Payment


# ---------------- ADMIN AUTH ----------------

def admin_login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('administrator:dashboard')
        else:
            return render(request, 'admin_login.html', {
                'error': 'Invalid credentials or not staff'
            })
    return render(request, 'admin_login.html')


def admin_login_page(request):
    return render(request, 'admin_login.html')


def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('admin_login')


# ---------------- BUS SEARCH ----------------

def bus_search(request):
    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')
    schedules = []

    if source and destination:
        schedules = Schedule.objects.select_related(
            'bus', 'route'
        ).filter(
            route__source__icontains=source,
            route__destination__icontains=destination
        )

        if departure_date:
            schedules = schedules.filter(
                departure_time__date=departure_date
            )

        for schedule in schedules:
            total_seats = Seat.objects.filter(
                bus=schedule.bus
            ).count()

            booked_count = Booking.objects.filter(
                schedule=schedule,
                status='Confirmed'
            ).count()

            schedule.available_seats = total_seats - booked_count
            schedule.is_sold_out = schedule.available_seats <= 0

    return render(request, 'busop_search.html', {
        'schedules': schedules,
        'source': source,
        'destination': destination,
        'departure_date': departure_date
    })


# ---------------- CREATE BOOKING ----------------

@login_required
def create_booking(request):
    schedule_id = request.GET.get('schedule_id')

    if not schedule_id:
        messages.error(request, "Invalid booking request.")
        return redirect('bus_search')

    schedule = get_object_or_404(Schedule, id=schedule_id)

    def get_available_seats():
        return Seat.objects.filter(
            bus=schedule.bus,
            is_available=True
        )

    if request.method == "POST":
        passenger_name = request.POST.get('passenger_name')
        passenger_email = request.POST.get('passenger_email')
        passenger_phone = request.POST.get('passenger_phone')
        seat_id = request.POST.get('seat')

        if not all([passenger_name, passenger_email, passenger_phone, seat_id]):
            return render(request, 'create_booking.html', {
                'schedule': schedule,
                'available_seats': get_available_seats(),
                'error': 'All fields are required.'
            })

        try:
            with transaction.atomic():
                seat = Seat.objects.select_for_update().get(
                    id=seat_id,
                    bus=schedule.bus,
                    is_available=True
                )

                booking = Booking.objects.create(
                    user=request.user,
                    schedule=schedule,
                    seat=seat,
                    passenger_name=passenger_name,
                    passenger_email=passenger_email,
                    passenger_phone=passenger_phone,
                    status='Confirmed'
                )

                Payment.objects.create(
                    booking=booking,
                    amount=schedule.price,
                    payment_status='Success'
                )

                seat.is_available = False
                seat.save(update_fields=['is_available'])

            messages.success(request, "🎉 Booking confirmed successfully!")
            return redirect('booking_history')

        except Seat.DoesNotExist:
            return render(request, 'create_booking.html', {
                'schedule': schedule,
                'available_seats': get_available_seats(),
                'error': 'Selected seat is no longer available.'
            })

        except Exception as e:
            print("BOOKING ERROR:", e)
            return render(request, 'create_booking.html', {
                'schedule': schedule,
                'available_seats': get_available_seats(),
                'error': str(e)
            })

    return render(request, 'create_booking.html', {
        'schedule': schedule,
        'available_seats': get_available_seats()
    })


# ---------------- BOOKING HISTORY ----------------

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        'schedule__bus', 'schedule__route', 'seat'
    ).order_by('-id')

    return render(request, 'booking_history.html', {
        'bookings': bookings
    })


# ---------------- CANCEL BOOKING ----------------

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.schedule.departure_time - timezone.now() < timezone.timedelta(hours=1):
        return render(request, 'cancel_error.html', {
            'error': 'Cannot cancel bookings less than 1 hour before departure.'
        })

    if booking.status == 'Confirmed':
        booking.status = 'Cancelled'
        booking.save(update_fields=['status'])

        Payment.objects.filter(
            booking=booking
        ).update(payment_status='Refunded')

        messages.success(
            request,
            f"Booking #{booking.id} has been cancelled successfully."
        )

    return redirect('booking_history')


# ---------------- INVOICE ----------------

@login_required
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
