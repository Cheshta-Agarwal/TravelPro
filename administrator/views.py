from django.shortcuts import render
from busop.models import Schedule
# Create your views here.

def busop_search(request):
    # use GET to allow bookmarking/sharing search results
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')

    schedules=[]
    if source and destination:
        schedules = Schedule.objects.select_related('bus', 'route').filter(
            route__source__icontains=source,
            route__destination__icontains=destination
            )
        
        if departure_date:
            schedules = schedules.filter(departure_time__date=departure_date)
        
        context ={
            'schedules': schedules,
            'source': source,
            'destination': destination,
            'departure_date': departure_date
        }

    return render(request, 'busop/bus_search.html', context)