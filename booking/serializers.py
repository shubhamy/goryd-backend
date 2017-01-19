from rest_framework import serializers, status
from rest_framework.exceptions import *
from .models import booking, bookingsPhoto, STATUS_TYPE_CHOICES, BookingDates
import hashlib
import random
import datetime
from listing.models import vehicle, availability, Address
from support.sendMailApi import *
from support.sendSmsApi import *
from threading import Thread
from users.serializers import *
from listing.serializers import *
from support.sendMailApi import send_on_new_booking
import string
from dateutil.relativedelta import relativedelta
from finance.views import *
from .tasks import *
import pytz

class bookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = booking
        fields = ('pk', 'vehicle', 'pickupTime' , 'dropTime', 'status', 'bookingId', 'totalCost', 'deposit', 'customer')

    def create(self, validated_data):
        b = booking(**validated_data)
        u = self.context['request'].user
        if u.ecommerceProfile.dob + relativedelta(years=23) > datetime.datetime.now().date():
            raise ValidationError({'error': 'Below 23'})
        if u.ecommerceProfile.dl:
            if u.ecommerceProfile.idProof:
                if not u.ecommerceProfile.isVerifiedRenter:
                    raise ValidationError({'error': 'We are verifying your profile. Please be patient.'})
                else:
                    pass
            else:
                raise ValidationError({'error': 'Upload your Id proof and become verified.'})
        else:
            raise ValidationError({'error': 'Upload your Driving License and become verified.'})


        data = self.context['request'].data
        car = vehicle.objects.get(pk=data['vehicle'])
        if u == car.owner:
            raise ValidationError({"error": "You are booking your own car"})
        b.vehicle = car
        b.pickupLoc = car.address
        b.dropLoc = car.address
        b.customer = u
        if data['status'] == STATUS_TYPE_CHOICES[0][0]:
            b.status = data['status']

        ## validation date time values
        try:
            pt = datetime.datetime.strptime( data['from'], "%Y-%m-%dT%H:%M")
            dt = datetime.datetime.strptime( data['to'], "%Y-%m-%dT%H:%M")
            if pt < dt:
                b.pickupTime = pt
                b.dropTime = dt
            else:
                raise ValidationError("Booking Cannot be made.")
        except Exception, e:
            raise ValidationError("Invalid Date Time Values")

        ## calculating total cost and deposit
        b.totalCost = calculate_total_rent(car.weekdayPrice, car.weekendPrice, b.pickupTime, b.dropTime)
        b.deposit = car.deposit

        ## generating booking ID
        m = hashlib.md5()
        m.update(str(u.email)+str(random.random()))
        bookingId = string.upper(m.hexdigest()[:6])
        while booking.objects.filter(bookingId=bookingId).exists():
            m = hashlib.md5()
            m.update(str(u.email)+str(random.random()))
            bookingId = m.hexdigest()[:6]
        b.bookingId = bookingId

        zone = pytz.timezone('Asia/Kolkata')
        if b.pickupTime >= datetime.datetime.now() + datetime.timedelta(hours=1):
            eta=zone.localize(datetime.datetime.now()+datetime.timedelta(hours=1))
            cancel_after_one_hour.apply_async((bookingSerializer(b).data,), eta=eta, expires=eta+datetime.timedelta(seconds=120))
            if b.pickupTime >= datetime.datetime.now() + datetime.timedelta(hours=12):
                eta=zone.localize(b.pickupTime-datetime.timedelta(hours=12))
                send_notification_and_location.apply_async((bookingSerializer(b).data,), eta=eta, expires=eta+datetime.timedelta(seconds=120))
            else:
                eta=zone.localize(datetime.datetime.now()+datetime.timedelta(seconds=120))# waits for booking object to get saved
                send_notification_and_location.apply_async((bookingSerializer(b).data,), eta=eta, expires=eta+datetime.timedelta(seconds=120))
        else:
            raise ValidationError({'error': 'pickup time is too early'})

        try:
            content = {
                'name': b.customer.first_name,
                'bookingID': b.bookingId,
                'fromDateTime': str(b.pickupTime),
                'toDateTime': str(b.dropTime),
                'bookingDate': str(datetime.datetime.now().date()),
                'status': b.status,
                'carMakeModel': str(b.vehicle.maker)+', '+str(b.vehicle.model),
                'totalRent': b.totalCost,
                'deposit': '',
                'pickupLoc': b.pickupLoc,
            }
            t = Thread(target=send_on_new_booking, kwargs={'email': b.customer.email, 'content': content, 'email_templates': 'booking-requested-renter.html'})
            t.start()
            t = Thread(target=send_sms_on_booking(b.customer.ecommerceProfile.mobile, b.customer.first_name, b.bookingId))
            t.start()
            content = {
                'name': b.vehicle.owner.first_name,
                'renterName': b.customer.first_name+' '+b.customer.last_name,
                'bookingID': b.bookingId,
                'fromDateTime': str(b.pickupTime),
                'toDateTime': str(b.dropTime),
                'bookingDate': str(datetime.datetime.now().date()),
                'status': b.status,
                'carMakeModel': str(b.vehicle.maker)+', '+str(b.vehicle.model),
                'totalRent': b.totalCost,
                'deposit': '',
                'pickupLoc': b.pickupLoc,
            }
            t = Thread(target=send_on_new_booking, kwargs={'email': b.vehicle.owner.email, 'content': content, 'email_templates': 'booking-requested-owner.html'})
            t.start()
            t = Thread(target=send_sms_to_owner_on_booking(b.vehicle.owner.ecommerceProfile.mobile, b.vehicle.owner.first_name, b.customer.first_name))
            t.start()
        except Exception, e:
            print e

        ##updating availabilities and bookingdates
        make_unavailable(b)
        b.save()
        return b

class bookingsPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = bookingsPhoto
        fields = ('pk' , 'photo' , 'booking' , 'text' , 'uploader' )

class BookingDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDates
