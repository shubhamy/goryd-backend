from __future__ import unicode_literals

from django.db import models
from users.models import userReviewComment
from django.contrib.auth.models import User
from finance.models import payment , Coupon
from django.db.models.signals import post_save , pre_delete
from django.dispatch import receiver
from PIL import Image
import os
import datetime
from time import time

MEDIA_TYPE_CHOICES = (
    ('onlineVideo' , 'onlineVideo'),
    ('video' , 'video'),
    ('image' , 'image'),
    ('onlineImage' , 'onlineImage'),
    ('doc' , 'doc'),
)

GEAR_CHOICES = (
    ('Manual', 'Manual'),
    ('Automatic', 'Automatic')
)

def getCarPhotosUploadPath(instance , filename):
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join(instance.user.username,'listing', 'vehicle', instance.vehicle.pk))
        return os.path.join(instance.user.username, 'listing','vehicle', str(instance.vehicle.pk), filename)
    except:
        return os.path.join(instance.user.username, 'listing','vehicle', str(instance.vehicle.pk), filename)

class Address(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    street = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=50, null=True)
    pincode = models.PositiveIntegerField(null=True)
    lat = models.CharField(max_length=50, null=True)
    lon = models.CharField(max_length=50, null=True)
    createdBy = models.ForeignKey(User, null=True, related_name='address')

    def __unicode__(self):
        return str(self.street) + ', ' + str(self.city) + ', ' + str(self.state) + ', ' + str(self.pincode)

class Maker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    maker = models.CharField(max_length=150, null=False, unique=True)

    def __unicode__(self):
        return self.maker

class Model(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=150, null=False, unique=True)
    maker = models.ForeignKey(Maker, null=False)

    def __unicode__(self):
        return self.model

class vehicle(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, null=True, related_name='listedVehicles')
    model  = models.ForeignKey(Model, null=False, related_name='vehicle')
    maker = models.ForeignKey(Maker, null=False, related_name='vehicle')
    regNum = models.CharField(null=True, max_length=100, unique=True)
    year = models.PositiveIntegerField(null=False, default=2000)
    kms = models.PositiveIntegerField(null=False, default=0)
    gearType = models.CharField(max_length=150, choices=GEAR_CHOICES, null=False, default='manual')
    address = models.ForeignKey(Address, null=True, related_name='vehicle')

    weekdayPrice = models.PositiveIntegerField(default=0, null=False)
    weekendPrice = models.PositiveIntegerField(default=0, null=False)
    deposit = models.PositiveIntegerField(default=3000, null=False)

    isListingComplete = models.BooleanField(default=False)
    active = models.BooleanField(default=False) # whether active by owner. Because owner has responsibility to deactivate it anytime they want
    verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0)
    totalBookings = models.PositiveIntegerField(default=0)
    totalEarning = models.FloatField(default=0)

    def __unicode__(self):
        return str(self.regNum) + ', ' + str(self.model) + ' by ' + str(self.owner)

class Media(models.Model):
    user = models.ForeignKey(User, related_name = 'projectsUploads' , null = False)
    created = models.DateTimeField(auto_now_add = True)
    link = models.TextField(null = True , max_length = 300) # can be youtube link or an image link
    attachment = models.FileField(upload_to = getCarPhotosUploadPath , null = True )
    mediaType = models.CharField(choices = MEDIA_TYPE_CHOICES , max_length = 10 , default = 'image')
    name = models.CharField(max_length = 100 , null = True)
    vehicle = models.ForeignKey(vehicle , null = True, related_name='photos')

class availability(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    vehicle = models.ManyToManyField(vehicle, related_name = 'availabilities')
    date = models.DateField(default=datetime.datetime.now)
    class Meta:
        verbose_name = "availability"
        verbose_name_plural = "availabilities"
    def __unicode__(self):
        return str(self.date)

class vehicleReviewComment(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    text = models.CharField(max_length = 300 , blank = False)
    reviewer = models.ForeignKey(User , null = False , related_name='userReviewComments')
    vehicle = models.ForeignKey(vehicle , null = False , related_name='comments')
    rating = models.PositiveIntegerField(null = True, default=0)

    def __unicode__(self):
        return "Rating: "+str(self.rating)+" Reviews: "+self.text

class AreaPincode(models.Model):
    officeName = models.CharField(null=True, max_length=300)
    pincode = models.PositiveIntegerField(null=True)
    stateName = models.CharField(max_length=50, null=True)
    districtName = models.CharField(max_length=100, null=True)
    taluk = models.CharField(max_length=100, null=True)
