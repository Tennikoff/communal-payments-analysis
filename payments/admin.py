from django.contrib import admin
from .models import ServiceType, Apartment, Tariff, PaymentRecord, UserServiceNorm


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'norm_per_person')
    search_fields = ('name',)


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('address', 'user', 'area', 'residents_count', 'created_at')
    search_fields = ('address', 'user__username')
    list_filter = ('created_at',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'region', 'price', 'valid_from', 'valid_to')
    search_fields = ('region', 'service_type__name')
    list_filter = ('service_type', 'region')


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'service_type', 'date', 'consumption', 'total_amount', 'is_overpayment')
    search_fields = ('apartment__address',)
    list_filter = ('service_type', 'is_overpayment', 'date')
    date_hierarchy = 'date'


@admin.register(UserServiceNorm)
class UserServiceNormAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'norm_per_person')
    search_fields = ('user__username', 'service_type__name')
    list_filter = ('service_type',)
