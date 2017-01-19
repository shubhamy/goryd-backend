from django.contrib import admin
from .models import *
from django.contrib.admin import SimpleListFilter
from daterange_filter.filter import DateRangeFilter
from django.utils.html import format_html

class ErrorFilter(SimpleListFilter):
    title = 'Error'
    parameter_name = 'error'

    def lookups(self, request, model_admin):
        return (
            ('mail_error', 'Mail Not Sent'),
            ('payment_error', 'Incomplete Transaction')
        )

    def queryset(self, request, queryset):
        if self.value() == 'mail_error':
            return queryset.filter(error="Mail cannot be sent")
        elif self.value() == 'payment_error':
            return queryset.filter(error="Incomplete Transaction")

class bookingAdmin(admin.ModelAdmin):
    list_display = ('created', 'bookingId', 'vehicle', 'customer', 'pickupLoc', 'dropLoc', 'pickupTime', 'dropTime','totalCost', 'comment', 'userReview', 'startOdometer', 'endOdometer', 'status', 'payment', 'coupon', 'error', 'ownerComment')
    list_filter = ('status',('pickupTime', DateRangeFilter), ErrorFilter)
    search_fields = ('bookingId',)

class bookingsPhotoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'booking', 'photo', 'text', 'uploader')

class BookingDatesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'list_of_vehicles')
    list_filter = (('date', DateRangeFilter),)
    date_hierarchy = 'date'
    def list_of_vehicles(self, obj):
        return format_html("<br><br>".join([str(v.model)+' ('+str(v.regNum)+') owned by '+str(v.owner.email) for v in obj.vehicle.all()]))

admin.site.register(booking, bookingAdmin)
admin.site.register(bookingsPhoto, bookingsPhotoAdmin)
admin.site.register(BookingDates, BookingDatesAdmin)
