from django.db.models import Count, Sum
from user.models import Payment, Booking
from busop.models import Bus, Schedule

def admin_report():
    report={
        'total_revenue': Payment.objects.filter(status='completed').aggregate(total=Sum('amount')),
        'total_bookings': Booking.objects.count(),
        'bookings_by_status': Booking.objects.values('status').annotate(count=Count('id')),
        'popular_destinations': Booking.objects.values('destination').annotate(count=Count('id')).order_by('-count'),
    }
    return report

def get_admin_dashboard_stats():
    stats = {
        # Calculate total successful revenue
        'total_revenue': Payment.objects.filter(
            payment_status='Success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0,

        # Count total active bookings
        'total_bookings': Booking.objects.filter(status='Confirmed').count(),

        # Count total fleet size
        'total_buses': Bus.objects.count(),

        # Advanced Query: Group bookings by route to find the most popular path
        'top_routes': Booking.objects.values(
            'schedule__route__source', 
            'schedule__route__destination'
        ).annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')[:5]
    }
    return stats