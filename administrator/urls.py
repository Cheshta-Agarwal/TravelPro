from django.urls import path
from .views import (
    AdminDashboardView,
    BusListView, BusCreateView, BusUpdateView, BusDeleteView,
    RouteListView, RouteCreateView, RouteUpdateView, RouteDeleteView,
)

app_name = "administrator"

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="dashboard"),

    # Bus management
    path("buses/", BusListView.as_view(), name="bus_list"),
    path("buses/create/", BusCreateView.as_view(), name="bus_create"),
    path("buses/<int:pk>/edit/", BusUpdateView.as_view(), name="bus_edit"),
    path("buses/<int:pk>/delete/", BusDeleteView.as_view(), name="bus_delete"),

    # Route management
    path("routes/", RouteListView.as_view(), name="route_list"),
    path("routes/create/", RouteCreateView.as_view(), name="route_create"),
    path("routes/<int:pk>/edit/", RouteUpdateView.as_view(), name="route_edit"),
    path("routes/<int:pk>/delete/", RouteDeleteView.as_view(), name="route_delete"),
]
