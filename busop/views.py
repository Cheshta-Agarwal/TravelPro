from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from busop.models import Schedule, Seat, Stop
from user.models import Booking, Payment


# ================= ADMIN AUTH =================

def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user and user.is_staff:
            login(request, user)
            return redirect("administrator:dashboard")
        return render(request, "admin_login.html", {
            "error": "Invalid credentials or not staff"
        })
    return render(request, "admin_login.html")


def admin_login_page(request):
    return render(request, "admin_login.html")


def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("admin_login")


# ================= BUS SEARCH =================

def bus_search(request):
    source = request.GET.get("source")
    destination = request.GET.get("destination")
    departure_date = request.GET.get("departure_date")

    schedules = Schedule.objects.select_related(
        "bus", "route"
    ).prefetch_related(
        "route__stops"
    )

    valid_schedules = []

    if source and destination:
        for schedule in schedules:
            # Build station list: source -> stops -> destination
            stations = [schedule.route.source]
            stations += [s.location_name for s in schedule.route.stops.all()]
            stations.append(schedule.route.destination)

            if source in stations and destination in stations:
                if stations.index(source) < stations.index(destination):
                    valid_schedules.append(schedule)
    else:
        valid_schedules = schedules

    if departure_date:
        valid_schedules = [
            s for s in valid_schedules
            if s.departure_time.date().isoformat() == departure_date
        ]

    # Attach availability
    for schedule in valid_schedules:
        total = Seat.objects.filter(bus=schedule.bus).count()
        booked = Booking.objects.filter(
            schedule=schedule,
            status="Confirmed"
        ).count()
        schedule.available_seats = total - booked
        schedule.is_sold_out = schedule.available_seats <= 0

    return render(request, "busop_search.html", {
        "schedules": valid_schedules,
        "source": source,
        "destination": destination,
        "departure_date": departure_date
    })


# ================= CREATE BOOKING =================

# ================= CREATE BOOKING =================

@login_required
def create_booking(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    # Get all seats for this bus
    all_seats = Seat.objects.filter(
        bus=schedule.bus
    ).order_by("seat_number")

    # Get booked seat IDs for this schedule
    booked_seat_ids = Booking.objects.filter(
        schedule=schedule,
        status="Confirmed"
    ).values_list('seat_id', flat=True)

    # Create a list of seats with their availability status
    seats_with_status = []
    for seat in all_seats:
        seat.is_booked = seat.id in booked_seat_ids
        seats_with_status.append(seat)

    # Get only available seats for selection
    available_seats = [seat for seat in seats_with_status if not seat.is_booked]

    route_stops = schedule.route.stops.all().order_by("stop_order")

    # Tiered pricing logic
    discount_map = {
        1: Decimal("0.60"),  # 40% off
        2: Decimal("0.75"),  # 25% off
    }
    default_discount = Decimal("0.90")  # 10% off

    # Handle POST request (form submission)
    if request.method == "POST":
        seat_id = request.POST.get("seat")
        stop_id = request.POST.get("drop_off_point")
        passenger_name = request.POST.get("passenger_name")
        passenger_email = request.POST.get("passenger_email")
        passenger_phone = request.POST.get("passenger_phone")

        if not all([seat_id, passenger_name, passenger_email, passenger_phone]):
            messages.error(request, "All fields are required.")
            return redirect(request.path)

        selected_stop = None
        final_fare = schedule.price

        if stop_id:
            selected_stop = get_object_or_404(Stop, id=stop_id)
            factor = discount_map.get(
                selected_stop.stop_order,
                default_discount
            )
            final_fare = (schedule.price * factor).quantize(
                Decimal("1.00")
            )

        try:
            with transaction.atomic():
                # Verify seat is still available
                selected_seat = Seat.objects.select_for_update().get(
                    id=seat_id,
                    bus=schedule.bus,
                    is_available=True
                )

                # Double-check no booking exists
                existing_booking = Booking.objects.filter(
                    schedule=schedule,
                    seat=selected_seat,
                    status="Confirmed"
                ).exists()
                
                if existing_booking:
                    raise Seat.DoesNotExist

                booking = Booking.objects.create(
                    user=request.user,
                    schedule=schedule,
                    seat=selected_seat,
                    passenger_name=passenger_name,
                    passenger_email=passenger_email,
                    passenger_phone=passenger_phone,
                    status="Confirmed"
                )

                selected_seat.is_available = False
                selected_seat.save(update_fields=["is_available"])

                Payment.objects.create(
                    booking=booking,
                    amount=final_fare,
                    payment_method="Direct",
                    payment_status="Completed"
                )

            send_mail(
    subject="Booking Confirmation - TravelPro",
    message=(
        f"Hi {request.user.username},\n\n"
        f"Your booking has been successfully confirmed!\n\n"
        f"Bus Number: {schedule.bus.bus_number}\n"
        f"Route: {schedule.route.source} to {schedule.route.destination}\n"
        f"Departure: {schedule.departure_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"Seat Number: {selected_seat.seat_number}\n"
        f"Fare Paid: ₹{final_fare}\n\n"
        f"Thank you for choosing TravelPro.\n"
        f"Have a safe journey!"
    ),
    from_email=settings.EMAIL_HOST_USER,
    recipient_list=[request.user.email],
    fail_silently=False,
) 
            return redirect("booking_history")       

        except Seat.DoesNotExist:
            messages.error(
                request,
                "Seat already booked. Please choose another."
            )
            return redirect(request.path)

    # Prepare stop dropdown with prices (for GET request)
    stops_with_prices = []
    for stop in route_stops:
        factor = discount_map.get(stop.stop_order, default_discount)
        price = (schedule.price * factor).quantize(Decimal("1.00"))
        stops_with_prices.append({
            "id": stop.id,
            "name": stop.location_name,
            "price": price
        })

    # For GET request, just render the page
    return render(request, "create_booking.html", {
        "schedule": schedule,
        "all_seats": seats_with_status,
        "available_seats": available_seats,
        "booked_seat_ids": list(booked_seat_ids),
        "stops_with_prices": stops_with_prices
    })


# ================= BOOKING HISTORY =================

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        "schedule__bus",
        "schedule__route",
        "seat"
    ).prefetch_related(
        "payment_set"
    ).order_by("-id")

    return render(request, "booking_history.html", {
        "bookings": bookings
    })


# ================= CANCEL BOOKING =================

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.schedule.departure_time - timezone.now() < timezone.timedelta(hours=1):
        return render(request, "cancel_error.html", {
            "error": "Cancellations not allowed within 1 hour of departure."
        })

    if booking.status != "Cancelled":
        booking.status = "Cancelled"
        booking.save(update_fields=["status"])

        seat = booking.seat
        seat.is_available = True
        seat.save(update_fields=["is_available"])

        Payment.objects.filter(
            booking=booking
        ).update(payment_status="Refunded")

        messages.success(
            request,
            f"Booking #{booking.id} cancelled. Seat {seat.seat_number} released."
        )

    return redirect("booking_history")


# ================= INVOICE =================

@login_required
def generate_invoice(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )
    payment = Payment.objects.filter(booking=booking).first()

    return render(request, "invoice.html", {
        "booking": booking,
        "payment": payment,
        "bus": booking.schedule.bus,
        "route": booking.schedule.route,
        "schedule": booking.schedule,
        "seat": booking.seat,
    })
