from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from rest_framework.response import Response
from listing.serializers import addressSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon

class paymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment
        fields = ('pk','created','paymentMode','status','transaction')
