from django.contrib import admin
from .models import *
from django.contrib.admin import SimpleListFilter
import datetime
from dateutil.relativedelta import relativedelta

class AgeFilter(SimpleListFilter):
    title = 'Age'
    parameter_name = 'dob'

    def lookups(self, request, model_admin):
        return (
            ('adult', 'Equal or Above 23'),
            ('child', 'Below 23')
        )

    def queryset(self, request, queryset):
        if self.value() == 'adult':
            return queryset.filter(dob__lte=(datetime.datetime.now().date() - relativedelta(years=23)))
        elif self.value() == 'child':
            return queryset.filter(dob__gt=(datetime.datetime.now().date() - relativedelta(years=23)))

# Register your models here.
class profileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mobile', 'dl', 'dp', 'idProof', 'user', 'dob', 'rating', 'isOwner', 'isVerifiedRenter', 'isMobileVerified', 'otp')
    date_hierarchy = 'created'
    search_fields = ('^user__username', )
    list_filter = ('isOwner', 'isVerifiedRenter', 'isMobileVerified', AgeFilter)
    list_editable = ('isOwner', 'isVerifiedRenter')

class userReviewCommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'rating', 'profile', 'reviewer')
    date_hierarchy = 'created'

class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')

admin.site.register(profile, profileAdmin)
admin.site.register(userReviewComment, userReviewCommentAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
