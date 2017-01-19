from django.contrib import admin
from .models import *
from daterange_filter.filter import DateRangeFilter
from django.utils.html import format_html

class AddressAdmin(admin.ModelAdmin):
    list_display = ('pk', 'street', 'city', 'state', 'pincode', 'lat', 'lon', 'createdBy')
    search_fields = ('^state', '^city', '^createdBy__username', '^pincode')
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AddressAdmin, self).get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(pincode=search_term_as_int)
        return queryset, use_distinct

class MakerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'maker')
    search_fields = ('maker',)

class ModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'model', 'maker')
    list_filter = ('maker',)
    search_fields = ('model',)

class vehicleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'maker', 'model', 'regNum', 'owner', 'weekdayPrice', 'weekendPrice', 'deposit', 'rating', 'active', 'verified', 'isListingComplete', 'totalBookings', 'totalEarning', 'year', 'kms', 'gearType', 'address')
    actions =['makeVerified', 'makeActive']
    list_editable = ('verified',)
    search_fields = ('^regNum', '^owner__username', '^maker__maker', '^model__model')
    list_filter = ('active', 'verified', 'isListingComplete', 'gearType')
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ('maker', 'model', 'regNum', 'owner', 'year', 'kms', 'gearType', 'address', 'active', 'isListingComplete')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('rating', 'totalBookings', 'totalEarning', 'weekdayPrice', 'weekendPrice', 'deposit', 'verified'),
        }),
    )

    def makeActive(self, request, queryset):
        vehicles_updated = queryset.update(active=True)
        if vehicles_updated == 1:
            message_bit = "1 listing was"
        else:
            message_bit = "%s listings were" % vehicles_updated
        self.message_user(request, "%s successfully marked as active." % message_bit)
    makeActive.short_description = "Listing Status: Active"

    def makeVerified(self, request,queryset):
        vehicles_updated = queryset.update(verified=True)
        if vehicles_updated == 1:
            message_bit = "1 listing was"
        else:
            message_bit = "%s listings were" % vehicles_updated
        self.message_user(request, "%s successfully marked as reviewing." % message_bit)
    makeVerified.short_description = "Listing Status: Verified"

class MediaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'link', 'attachment', 'mediaType', 'name', 'vehicle')
    search_fields = ('^user__username', '=vehicle__regNum', '^vehicle__maker__maker', '^vehicle__model__model')

class availabilityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date', 'list_of_vehicles')
    list_filter = (('date', DateRangeFilter),)
    date_hierarchy = 'date'
    def list_of_vehicles(self, obj):
        return format_html("<br><br>".join([str(v.model)+' ('+str(v.regNum)+') by '+str(v.owner.email) for v in obj.vehicle.all()]))

class vehicleReviewCommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'reviewer', 'text', 'vehicle', 'rating')
    
class AreaPincodeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'officeName', 'pincode', 'stateName', 'districtName', 'taluk')

admin.site.register(Address, AddressAdmin)
admin.site.register(vehicle, vehicleAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(availability, availabilityAdmin)
admin.site.register(vehicleReviewComment, vehicleReviewCommentAdmin)
admin.site.register(Maker, MakerAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(AreaPincode, AreaPincodeAdmin)