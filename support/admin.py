from django.contrib import admin
from .models import *

# Register your models here.

class ticketAdmin(admin.ModelAdmin):
    list_display = ('ticketID', 'created', 'priorityLevel', 'status', 'category', 'user', 'subject', 'description')
    list_filter = ('status', 'priorityLevel', 'category__category')
    list_display_links = None
    list_editable = ('priorityLevel',)
    date_hierarchy = 'created'
    search_fields = ('user__username', 'ticketID', 'category__name')
    actions = ['reviewingStatus', 'resolvedStatus']

    def reviewingStatus(self, request, queryset):
        tickets_updated = queryset.update(status= 'reviewing')
        if tickets_updated == 1:
            message_bit = "1 ticket was"
        else:
            message_bit = "%s tickets were" % tickets_updated
        self.message_user(request, "%s successfully marked as reviewing." % message_bit)
    reviewingStatus.short_description = "Ticket Status: Reviewing"

    def resolvedStatus(self, request, queryset):
        tickets_updated = queryset.update(status= 'resolved')
        if tickets_updated == 1:
            message_bit = "1 ticket was"
        else:
            message_bit = "%s tickets were" % tickets_updated
        self.message_user(request, "%s successfully marked as reresolved." % message_bit)
    resolvedStatus.short_description = "Ticket Status: Resolved"

class faqAdmin(admin.ModelAdmin):
    list_display = ('subject', 'question', 'answer')
    list_filter = ('subject',)

class feedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'message', 'rating')

class subscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed')

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category')

class UserQueryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'email', 'fullname', 'query', 'status', 'verified')
    list_filter = ('status', 'verified')
    search_fields = ('email',)
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ('email', 'fullname', 'query')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('status', 'verified'),
        }),
    )

admin.site.register(ticket, ticketAdmin)
admin.site.register(faq, faqAdmin)
admin.site.register(feedback, feedbackAdmin)
admin.site.register(subscriber, subscriberAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(UserQuery, UserQueryAdmin)
