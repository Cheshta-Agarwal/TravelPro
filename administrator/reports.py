from django.db.models import Count, Sum
from user.models import Payment, Booking

def admin_report():
    report={
        'total_revenue': Payment.objects.filter(status='completed').aggregate(total=Sum('amount')),
        'total_bookings': Booking.objects.count(),
        'bookings_by_status': Booking.objects.values('status').annotate(count=Count('id')),
        'popular_destinations': Booking.objects.values('destination').annotate(count=Count('id')).order_by('-count'),
    }
    return report