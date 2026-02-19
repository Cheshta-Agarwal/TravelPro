from django.contrib import admin
from administrator.models import admin_user
# Register your models here.


@admin.register(admin_user)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone')
    search_fields = ('username', 'email')