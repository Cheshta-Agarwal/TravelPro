from django.shortcuts import render

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
        # Optimized with select_related for < 3s response time
        schedules = Schedule.objects.select_related('bus', 'route').filter(
            route__source__icontains=source,
            route__destination__icontains=destination
        )
        if departure_date:
            schedules = schedules.filter(departure_time__date=departure_date)

    # 3. Define the context OUTSIDE the if blocks
    context = {
        'schedules': schedules,
        'source': source,
        'destination': destination,
        'departure_date': departure_date
    }

    return render(request, 'busop_search.html', context)