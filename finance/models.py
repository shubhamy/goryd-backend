from __future__ import unicode_literals

from django.db import models
from users.models import profile

# Create your models here.
PAYMENT_STATUS_CHOICES = (
    ('notPaid', 'Not Paid'),
    ('paidOnline', 'Paid Online'),
    ('paidCash', 'Paid Cash'),
    ('received', 'Received'),
)
PAYMENT_TYPE_CHOICES = (
    ('cash', 'Not Listed'),
    ('debitCard', 'Debit Card'),
    ('creditCard', 'Credit Card'),
)

COUPON_TYPE_CHOICES = (
    ('TimeBased', 'TimeBased'),         #discount till T days and time
    ('depositBased', 'depositBased'),   #discount on security deposit
    ('bookingBased', 'bookingBased'),   #discount on next N bookings
)

CURRENCY_TYPE_CHOICES = (
    ('Percentage', 'Percentage'),
    ('Rupees', 'Rupees')
)

class Coupon(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    description = models.CharField(max_length = 300 , blank = False)
    discountAmount = models.PositiveIntegerField(null = True)
    currency = models.CharField(max_length=20, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_CHOICES[0][0], null=True)
    couponCode = models.CharField(max_length = 300 , blank = False)
    user = models.ForeignKey(profile, null=True, blank=True)
    startDate = models.DateTimeField(null=True)
    expiryDate = models.DateTimeField(null=True)
    isExpired = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    couponType = models.CharField(max_length=20, null=True, choices=COUPON_TYPE_CHOICES, default=COUPON_TYPE_CHOICES[0][0])
    
    def __unicode__(self):
        if self.currency == CURRENCY_TYPE_CHOICES[0][0]:
            return str(self.discountAmount) + '% discount' + ' ' + str(self.couponCode)
        elif self.currency == CURRENCY_TYPE_CHOICES[1][0]:
            return str(self.discountAmount) + ' discount' + ' ' + str(self.couponCode)

class payment(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    amount = models.FloatField(null = True)
    paymentMode = models.CharField(null = True, choices=PAYMENT_TYPE_CHOICES, default='notListed', max_length=10)
    status = models.CharField(null = True, choices=PAYMENT_STATUS_CHOICES, default='notListed', max_length=10)
    transaction = models.CharField( max_length = 300, blank = False)

    def __unicode__(self):
        return self.transaction + ": Rs. " + str(self.amount)
