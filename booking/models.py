from __future__ import unicode_literals

from django.db import models
from users.models import userReviewComment
from django.contrib.auth.models import User
from time import time
from finance.models import payment , Coupon
from django.db.models.signals import post_save , pre_delete
from PIL import Image
import os
from listing.models import *

def getBookingPicturePath(instance, filename):
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join('bookings', instance.booking.bookingId))
        return os.path.join('bookings', instance.booking.bookingId, filename)
    except:
        return os.path.join('bookings', instance.booking.bookingId, filename)

STATUS_TYPE_CHOICES = (
    ('requested', 'requested'),
    ('approved', 'approved'),
    ('ongoing', 'ongoing'),
    ('completed', 'completed'),
    ('cancelled', 'cancelled'),
    ('rejected', 'rejected')
)

class booking(models.Model):
    created = models.DateTimeField(auto_now_add = True, null=True)
    lastUpdated = models.DateTimeField(auto_now = True, null = True)
    vehicle = models.ForeignKey(vehicle, related_name= 'bookings', null = True)
    customer = models.ForeignKey(User, related_name='pastBooking', null = True)
    pickupLoc = models.ForeignKey(Address, related_name='bookingsStart', null = True)
    dropLoc = models.ForeignKey(Address, related_name='bookingsEnd', null = True)
    pickupTime = models.DateTimeField(blank= True)
    dropTime = models.DateTimeField(blank= True)
    totalCost = models.FloatField(null = True)
    deposit = models.PositiveIntegerField(null=True, default=3000)
    comment = models.ForeignKey(vehicleReviewComment, related_name = 'vehicleReview', null = True)
    userReview = models.ForeignKey(userReviewComment, related_name = 'userReview', null = True)
    startOdometer  = models.PositiveIntegerField(null= True)
    endOdometer  = models.PositiveIntegerField(null= True)
    status = models.CharField(null = True, choices=STATUS_TYPE_CHOICES, max_length=10)
    payment = models.ForeignKey(payment, related_name= 'bookings', null = True)
    coupon = models.ForeignKey(Coupon, null = True)
    bookingId = models.CharField(null=True, max_length=40, unique=True)
    ownerComment = models.TextField(null=True, max_length=300)
    error = models.TextField(null=True, max_length=300)

    def __unicode__(self):
        return self.bookingId

PHOTO_UPLOADER_CHOICES = (
    ('customer', 'customer'),
    ('owner', 'owner'),
    ('support', 'support'),
)

class bookingsPhoto(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    lastUpdated = models.DateTimeField(auto_now = True, null = True)
    photo = models.FileField(upload_to = getBookingPicturePath, null = True)
    booking = models.ForeignKey(booking, null=True, related_name='photos')
    text = models.CharField(max_length = 200 , null = True)
    uploader = models.CharField(choices = PHOTO_UPLOADER_CHOICES , default = 'customer' , max_length = 20)

class BookingDates(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    vehicle = models.ManyToManyField(vehicle, related_name='bookingDates')
    date = models.DateField(default=datetime.datetime.now)
    class Meta:
        verbose_name = "BookingDate"
        verbose_name_plural = "BookingDates"
    def __unicode__(self):
        return str(self.date)
