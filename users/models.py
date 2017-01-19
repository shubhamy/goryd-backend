from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from time import time
from django.utils import timezone
import datetime
import os
from backend import settings

MEDIA_TYPE_CHOICES = (
    ('onlineVideo' , 'onlineVideo'),
    ('video' , 'video'),
    ('image' , 'image'),
    ('onlineImage' , 'onlineImage'),
    ('doc' , 'doc'),
)

def getEcommercePictureUploadPath(instance , filename ):
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join(instance.user.username,'pictureUploads'))
        return os.path.join(instance.user.username, 'pictureUploads', filename)
    except:
        return os.path.join(instance.user.username, 'pictureUploads', filename)

def getDPUploadPath(instance , filename):
    if filename=='':
        filename = instance.user.username+"_fb_dp.jpeg"
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join(instance.user.username, 'DP'))
        return os.path.join(instance.user.username, 'DP', filename)
    except:
        return os.path.join(instance.user.username, 'DP', filename)

def getDLUploadPath(instance , filename):
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join(instance.user.username, 'DL'))
        return os.path.join(instance.user.username, 'DL', filename)
    except:
        return os.path.join(instance.user.username, 'DL', filename)

def getIdProofUploadPath(instance , filename):
    try:
        os.chdir(os.path.join(settings.BASE_DIR,'media_root'))
        os.mkdir(os.path.join(instance.user.username, 'idProof'))
        return os.path.join(instance.user.username, 'idProof', filename)
    except:
        return os.path.join(instance.user.username, 'idProof', filename)

class profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    mobile = models.CharField(null=True, unique=True, max_length=10)
    dl = models.FileField(null=True , upload_to=getDLUploadPath)
    dp = models.FileField(null=True , upload_to=getDPUploadPath)
    idProof = models.FileField(null=True , upload_to=getIdProofUploadPath)
    user = models.OneToOneField(User, related_name = 'ecommerceProfile', null=True)
    aboutMe = models.TextField(max_length=1000 , null=True)
    rating = models.FloatField(default=0)
    isOwner = models.BooleanField(default=False)
    isVerifiedRenter = models.BooleanField(default=False)
    isMobileVerified = models.BooleanField(default=False)
    dob = models.DateField(null=False, default=datetime.datetime.now)
    otp = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return self.user.get_full_name()

User.profile = property(lambda u : profile.objects.get_or_create(user = u)[0])

class userReviewComment(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    text = models.CharField(max_length = 300 , blank = False)
    profile = models.ForeignKey(profile , related_name='myReviews' , null = True)
    reviewer = models.ForeignKey(User , null = False , related_name='userReviewsWrote')
    rating = models.PositiveIntegerField(null=True, default=0)

    def __unicode__(self):
        return "Rating: "+str(self.rating)+" Reviews: "+self.text
