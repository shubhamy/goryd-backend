from django.contrib import admin
from .models import *

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'currency', 'discountAmount', 'couponCode', 'couponType', 'user', 'startDate', 'expiryDate', 'isExpired', 'isActive')
    list_filter = ('couponType', 'isExpired', 'isActive')
    search_fields = ('code', 'user__user__first_name')
    date_hierarchy = 'created'

class paymentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'amount', 'paymentMode', 'transaction', 'status')

admin.site.register(Coupon, CouponAdmin)
admin.site.register(payment, paymentAdmin)
