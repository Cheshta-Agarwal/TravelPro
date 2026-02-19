from django.urls import path
from .views import (
    AdminDashboardView,
    BusListView, BusCreateView, BusUpdateView, BusDeleteView,
    RouteListView, RouteCreateView, RouteUpdateView, RouteDeleteView,
    UserListView, UserDetailView, ScheduleDeleteView, ScheduleCreateView,ScheduleListView ,toggle_active_view, toggle_staff_view, delete_user_view,
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
    # User management (admin)
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/toggle-active/", toggle_active_view, name="toggle_active"),
    path("users/<int:pk>/toggle-staff/", toggle_staff_view, name="toggle_staff"),
    path("users/<int:pk>/delete/", delete_user_view, name="delete_user"),

    #Schedule Management
    path('schedules/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/add/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/delete/<int:pk>/', ScheduleDeleteView.as_view(), name='schedule_delete'),
]
