
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.db.models import Count, Sum, CharField, BooleanField
from django.apps import apps
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Prefetch
from .forms import BusForm, RouteForm



class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
	template_name = "administrator/dashboard.html"

	def test_func(self):
		return bool(self.request.user and self.request.user.is_staff)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# Total users
		context['total_users'] = User.objects.count()

		# Total buses and routes (from busop app)
		try:
			Bus = apps.get_model('busop', 'Bus')
			context['total_buses'] = Bus.objects.count()
		except LookupError:
			context['total_buses'] = 0

		try:
			Route = apps.get_model('busop', 'Route')
			context['total_routes'] = Route.objects.count()
		except LookupError:
			context['total_routes'] = 0

		# Bookings and revenue (booking lives in user app)
		total_bookings = 0
		total_revenue = 0

		try:
			Booking = apps.get_model('user', 'Booking')
		except LookupError:
			Booking = None

		if Booking is not None:
			booking_qs = Booking.objects.all()

			# If Booking has a 'status' field, try to filter for confirmed bookings
			status_field = None
			for f in Booking._meta.get_fields():
				if getattr(f, 'name', None) == 'status':
					status_field = f
					break

			if status_field is not None:
				if isinstance(status_field, BooleanField):
					booking_qs = booking_qs.filter(status=True)
				elif isinstance(status_field, CharField):
					booking_qs = booking_qs.filter(status__iexact='confirmed')

			total_bookings = booking_qs.count()

			# Revenue: prefer a total_amount on Booking if present, otherwise fall back to Payment.amount
			booking_fields = {f.name for f in Booking._meta.get_fields()}
			if 'total_amount' in booking_fields:
				total_revenue = booking_qs.aggregate(total=Sum('total_amount'))['total'] or 0
			else:
				try:
					Payment = apps.get_model('user', 'Payment')
					total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
				except LookupError:
					total_revenue = 0

		else:
			# If Booking model is missing, try Payments as best-effort
			try:
				Payment = apps.get_model('user', 'Payment')
				total_bookings = 0
				total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
			except LookupError:
				total_bookings = 0
				total_revenue = 0

		context['total_bookings'] = total_bookings
		context['total_revenue'] = total_revenue

		return context


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return bool(self.request.user and self.request.user.is_staff)


class BusListView(StaffRequiredMixin, ListView):
	template_name = 'administrator/bus_list.html'
	context_object_name = 'buses'
	paginate_by = 10

	def get_queryset(self):
		Bus = apps.get_model('busop', 'Bus')
		Schedule = apps.get_model('busop', 'Schedule')
		Seat = apps.get_model('busop', 'Seat')

		return Bus.objects.prefetch_related(
			Prefetch('schedule_set', queryset=Schedule.objects.select_related('route').order_by('departure_time'), to_attr='schedules_ordered'),
			Prefetch('seat_set', to_attr='seats_all')
		).all()


class BusCreateView(StaffRequiredMixin, CreateView):
	form_class = BusForm
	template_name = 'administrator/bus_form.html'
	success_url = reverse_lazy('administrator:bus_list')

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'Bus created successfully.')
		return response


class BusUpdateView(StaffRequiredMixin, UpdateView):
	form_class = BusForm
	template_name = 'administrator/bus_form.html'
	success_url = reverse_lazy('administrator:bus_list')

	def get_queryset(self):
		Bus = apps.get_model('busop', 'Bus')
		return Bus.objects.all()

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'Bus updated successfully.')
		return response


class BusDeleteView(StaffRequiredMixin, DeleteView):
	template_name = 'administrator/bus_confirm_delete.html'
	success_url = reverse_lazy('administrator:bus_list')

	def get_queryset(self):
		Bus = apps.get_model('busop', 'Bus')
		return Bus.objects.all()

	def delete(self, request, *args, **kwargs):
		messages.success(self.request, 'Bus deleted successfully.')
		return super().delete(request, *args, **kwargs)


class RouteListView(StaffRequiredMixin, ListView):
	template_name = 'administrator/route_list.html'
	context_object_name = 'routes'
	paginate_by = 10

	def get_queryset(self):
		Route = apps.get_model('busop', 'Route')
		return Route.objects.all()


class RouteCreateView(StaffRequiredMixin, CreateView):
	form_class = RouteForm
	template_name = 'administrator/route_form.html'
	success_url = reverse_lazy('administrator:route_list')

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'Route created successfully.')
		return response


class RouteUpdateView(StaffRequiredMixin, UpdateView):
	form_class = RouteForm
	template_name = 'administrator/route_form.html'
	success_url = reverse_lazy('administrator:route_list')

	def get_queryset(self):
		Route = apps.get_model('busop', 'Route')
		return Route.objects.all()

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'Route updated successfully.')
		return response


class RouteDeleteView(StaffRequiredMixin, DeleteView):
	template_name = 'administrator/route_confirm_delete.html'
	success_url = reverse_lazy('administrator:route_list')

	def get_queryset(self):
		Route = apps.get_model('busop', 'Route')
		return Route.objects.all()

	def delete(self, request, *args, **kwargs):
		messages.success(self.request, 'Route deleted successfully.')
		return super().delete(request, *args, **kwargs)

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from .forms import ScheduleForm  # We will create this next

class ScheduleListView(StaffRequiredMixin, ListView):
    template_name = 'administrator/schedule_list.html'
    context_object_name = 'schedules'
    
    def get_queryset(self):
        Schedule = apps.get_model('busop', 'Schedule')
        # Optimized with select_related to avoid N+1 queries for bus and route
        return Schedule.objects.select_related('bus', 'route').all().order_by('departure_time')

class ScheduleCreateView(StaffRequiredMixin, CreateView):
    form_class = ScheduleForm
    template_name = 'administrator/schedule_form.html'
    success_url = reverse_lazy('administrator:schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Schedule created successfully.')
        return super().form_valid(form)

class ScheduleDeleteView(StaffRequiredMixin, DeleteView):
    template_name = 'administrator/schedule_confirm_delete.html'
    success_url = reverse_lazy('administrator:schedule_list')
    
    def get_queryset(self):
        Schedule = apps.get_model('busop', 'Schedule')
        return Schedule.objects.all()

# -----------------------
# Administrator: User management
# -----------------------
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden



class UserListView(StaffRequiredMixin, ListView):
	template_name = 'administrator/user_list.html'
	context_object_name = 'users'
	paginate_by = 10

	def get_queryset(self):
		UserModel = get_user_model()
		# Order by most recent join; only load necessary fields to avoid extra cost
		return UserModel.objects.all().order_by('-date_joined').only('id', 'username', 'email', 'is_active', 'is_staff', 'date_joined')


class UserDetailView(StaffRequiredMixin, ListView):
	# Using ListView to keep things simple for template rendering; context will include `user_obj`
	template_name = 'administrator/user_detail.html'
	context_object_name = 'user_obj'

	def get(self, request, *args, **kwargs):
		UserModel = get_user_model()
		self.object = get_object_or_404(UserModel, pk=kwargs.get('pk'))
		return self.render_to_response(self.get_context_data())

	def get_context_data(self, **kwargs):
		context = {}
		user = self.object
		context['user_obj'] = user

		# Try to fetch bookings efficiently from possible apps (busop then user)
		Booking = None
		try:
			Booking = apps.get_model('busop', 'Booking')
		except LookupError:
			try:
				Booking = apps.get_model('user', 'Booking')
			except LookupError:
				Booking = None

		if Booking is not None:
			# Count bookings referencing this user (avoid loading booking objects)
			bookings_count = Booking.objects.filter(user_id=user.pk).count()
		else:
			bookings_count = 0

		context['bookings_count'] = bookings_count
		return context


def _staff_check(u):
	return bool(u and u.is_staff)


@login_required
@user_passes_test(_staff_check)
@require_POST
def toggle_active_view(request, pk):
	UserModel = get_user_model()
	target = get_object_or_404(UserModel, pk=pk)

	# Prevent self-deactivation
	if target.pk == request.user.pk:
		messages.error(request, 'You cannot change your own active status.')
		return redirect(reverse('administrator:user_list'))

	# Protect superuser unless current user is superuser
	if target.is_superuser and not request.user.is_superuser:
		messages.error(request, 'Cannot change active status of a superuser.')
		return redirect(reverse('administrator:user_list'))

	target.is_active = not target.is_active
	target.save(update_fields=['is_active'])
	messages.success(request, f"User '{target.username}' active status set to {target.is_active}.")
	return redirect(reverse('administrator:user_list'))


@login_required
@user_passes_test(_staff_check)
@require_POST
def toggle_staff_view(request, pk):
	UserModel = get_user_model()
	target = get_object_or_404(UserModel, pk=pk)

	# Prevent modifying own staff privilege
	if target.pk == request.user.pk:
		messages.error(request, 'You cannot change your own staff privileges.')
		return redirect(reverse('administrator:user_list'))

	# Protect removing staff from a superuser unless current user is superuser
	if target.is_superuser and not request.user.is_superuser:
		messages.error(request, 'Cannot change staff status of a superuser.')
		return redirect(reverse('administrator:user_list'))

	target.is_staff = not target.is_staff
	target.save(update_fields=['is_staff'])
	messages.success(request, f"User '{target.username}' staff status set to {target.is_staff}.")
	return redirect(reverse('administrator:user_list'))


@login_required
@user_passes_test(_staff_check)
@require_POST
def delete_user_view(request, pk):
	UserModel = get_user_model()
	target = get_object_or_404(UserModel, pk=pk)

	# Prevent deleting self
	if target.pk == request.user.pk:
		messages.error(request, 'You cannot delete your own account.')
		return redirect(reverse('administrator:user_list'))

	# Protect superuser unless current is superuser
	if target.is_superuser and not request.user.is_superuser:
		messages.error(request, 'Cannot delete a superuser.')
		return redirect(reverse('administrator:user_list'))

	# Hard delete only when explicitly requested and current user is superuser
	hard = request.POST.get('hard', '') == '1'
	if hard:
		if not request.user.is_superuser:
			messages.error(request, 'Only superusers may permanently delete users.')
			return redirect(reverse('administrator:user_list'))
		target.delete()
		messages.success(request, f"User '{target.username}' permanently deleted.")
		return redirect(reverse('administrator:user_list'))

	# Soft delete: deactivate account
	target.is_active = False
	target.save(update_fields=['is_active'])
	messages.success(request, f"User '{target.username}' deactivated (soft delete).")
	return redirect(reverse('administrator:user_list'))
