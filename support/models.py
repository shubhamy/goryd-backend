from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class feedback(models.Model):
    user = models.ForeignKey(User , null = True)
    created = models.DateTimeField(auto_now_add = True)
    message = models.CharField(max_length = 200 , null = False)
    rating = models.PositiveIntegerField(default=5)
    name = models.CharField(max_length = 50 , null = True)

STATUS_TYPE_CHOICES = (
    ('unresolved', 'Unresolved'),
    ('reviewing', 'Reviewing'),
    ('resolved', 'Resolved'),
)

PRIORITY_CHOICES = (
    ('none', 'None'),
    ('low', 'Low'),
    ('moderate', 'Moderate'),
    ('high', 'High'),
    ('critical', 'Critical'),
)

CATEGORY_CHOICES = (
    ('none', 'None'),
    ('Goryd Account', 'Goryd Account'),
    ('Booking', 'Booking'),
    ('Finance and Payment', 'Finance and Payment'),
    ('Vehicle Ownership', 'Vehicle Ownership'),
    ('Media', 'Media'),
)

class Subcategory(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=100, null=False, choices=CATEGORY_CHOICES, default='none')
    def __unicode__(self):
        return self.name

class ticket(models.Model):
    user = models.ForeignKey(User, null=True)
    created = models.DateTimeField(auto_now_add=True)
    ticketID = models.CharField(null = False, unique=True, max_length=50)
    category = models.ForeignKey(Subcategory, null=True)
    subject = models.CharField(max_length=100, null=True)
    description= models.CharField(max_length = 500, null=True)
    priorityLevel = models.CharField(max_length=100, null = False, choices=PRIORITY_CHOICES, default='none')
    status = models.CharField(max_length= 100, null= False, choices=STATUS_TYPE_CHOICES, default='unresolved')
    assignedTo = models.CharField(max_length=100, null=True, default=None)

FAQ_TYPE_CHOICES = (
    ('none', 'None'),
    ('account', 'Account'),
    ('booking', 'Booking'),
    ('listing', 'Listing'),
    ('payment', 'Payment'),
    ('refund', 'Refund'),
    ('carReturn', 'Car return'),
    ('insurance', 'Insurance'),
)

class faq(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    question = models.CharField(max_length=300, null=False)
    answer = models.CharField(max_length=1000, null=False)
    subject = models.CharField(max_length=100, null=False, choices=FAQ_TYPE_CHOICES, default='none')

class subscriber(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=50, null = False, unique=True)
    subscribed = models.BooleanField(default = False)

    def __unicode__(self):
        return self.email

class UserQuery(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    fullname = models.CharField(max_length=100, null=True)
    query = models.CharField(max_length = 500, null=True)
    email = models.CharField(max_length=50, null=False, default='support@goryd.in')
    status = models.BooleanField(default=True) #acitive or closed
    verified = models.BooleanField(default=False)
    class Meta:
        verbose_name = "User Query"
        verbose_name_plural = "User Queries"
