from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from rest_framework.response import Response
from django.http import HttpResponse
from users.serializers import userSerializer
import datetime
from users.serializers import *

class addressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["pk", "street", "city", "state", "pincode", "lat", "lon"]

    def create(self ,  validated_data):
        u = self.context['request'].user
        a = Address(**validated_data)
        a.createdBy = u
        a.save()
        return a

    def update(self , instance , validated_data):
        data = self.context['request'].data
        if all(i in data for i in ['lat', 'lon']):
            instance.lat = data['lat']
            instance.lon = data['lon']
            instance.save()
        elif all(i in data for i in ['street', 'city', 'state', 'pincode']):
            instance.street = data['street']
            instance.city = data['city']
            instance.state = data['state']
            instance.pincode = data['pincode']
            instance.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return instance

class availabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = availability
    def create(self, validated_data):
        r = self.context['request']
        v = vehicle.objects.get(pk=r.data['vehicle'][0])
        dates = r.data['dates']
        v.weekdayPrice = r.data['priceweekday']
        v.weekendPrice = r.data['priceweekend']
        v.deposit = r.data['deposit']
        v.save()
        for date in dates:
            try:
                availabilityObject = availability.objects.filter(date=date)[0]
            except:
                availabilityObject = availability.objects.create(date=datetime.datetime.strptime(date, "%Y-%m-%d"))
            availabilityObject.save()
            availabilityObject.vehicle.add(v)
        return availabilityObject

class MakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker

class ModelSerializer(serializers.ModelSerializer):
    maker = MakerSerializer(many=False, read_only=True)
    class Meta:
        model = Model

class vehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = vehicle
    def create(self , validated_data):
        v = vehicle(**validated_data)
        data = self.context['request'].data
        v.owner = self.context['request'].user
        v.maker = Maker.objects.get(pk = data['maker'])
        v.model = Model.objects.get(pk = data['model'])
        v.address = Address.objects.get(pk = data['address'])
        v.save()
        return v

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media

class vehicleReviewCommentSerializer(serializers.ModelSerializer):
    reviewer = userSerializer(read_only=True, many=False)
    class Meta:
        model = vehicleReviewComment
        fields = ['text', 'reviewer', 'rating']
        
class AreaPincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaPincode
