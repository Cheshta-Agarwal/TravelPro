from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.db.models import Count, Sum, CharField, BooleanField
from django.apps import apps


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