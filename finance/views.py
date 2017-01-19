from rest_framework import viewsets , permissions , serializers
from rest_framework.exceptions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from django.core import serializers
from django.http import JsonResponse
from API.permissions import *
from .serializers import *
import datetime

def given_date_rent(weekdayPrice, weekendPrice, givenDate):
    if givenDate.weekday() in [5,6]:
        return weekendPrice
    else:
        return weekdayPrice

def calculate_total_rent(weekdayPrice, weekendPrice, pickupTime, dropTime):
    totalRent = 0
    # weekday = [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday]
    pickupDayRent = ((24-pickupTime.hour)%24)*given_date_rent(weekdayPrice, weekendPrice, pickupTime)/24

    inBetweenDaysRent = 0
    if (24-pickupTime.hour)%24 == 0:
        inBetweenDays = pickupTime.date()
    else:
        inBetweenDays = pickupTime.date()+datetime.timedelta(days=1)
    while inBetweenDays < dropTime.date():
        inBetweenDaysRent += given_date_rent(weekdayPrice, weekendPrice, inBetweenDays)
        inBetweenDays += datetime.timedelta(days=1)

    if dropTime.minute != 0:
        dropDayRent = (dropTime.hour+1)*given_date_rent(weekdayPrice, weekendPrice, dropTime)/24
    else:
        dropDayRent = dropTime.hour*given_date_rent(weekdayPrice, weekendPrice, dropTime)/24

    totalRent = pickupDayRent + inBetweenDaysRent + dropDayRent

    return totalRent

class CouponViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()
    def list(self, request):
        try:
            p = profile.objects.get(user=request.user)
            retVal = []
            #couponData = CouponSerializer(Coupon.objects.filter(user=p), many=True).data
            #print couponData
            for c in Coupon.objects.filter(user=p):
                data = {
                    "pk": c.pk,
                    "code": c.code,
                    "description": c.description,
                }
                retVal.append(data)
            return Response(retVal)
        except:
            return

class paymentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = paymentSerializer
    queryset = payment.objects.all()
