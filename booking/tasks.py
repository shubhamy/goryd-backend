from __future__ import absolute_import
from celery import shared_task
from .models import STATUS_TYPE_CHOICES, booking, BookingDates
from support.sendMailApi import send_reminder
from support.sendSmsApi import send_reminder_sms_to_customer
from listing.models import availability
from threading import Thread
from users.models import profile
import datetime

def make_available(instance):
    for a in availability.objects.filter(date__range=[instance.pickupTime.date(), instance.dropTime.date()]):
        a.vehicle.add(instance.vehicle)
        bd = BookingDates.objects.filter(vehicle=instance.vehicle, date=a.date)[0]
        bd.vehicle.remove(instance.vehicle)
        a.save()

def make_unavailable(b):
    DAY = b.pickupTime.date().day
    for a in availability.objects.filter(vehicle=b.vehicle, date__range=[b.pickupTime.date(), b.dropTime.date()]):
        a.vehicle.remove(b.vehicle)
        day = a.date.day
        bd, isretrieved = BookingDates.objects.get_or_create(date=(b.pickupTime+datetime.timedelta(days=day%DAY)).date())
        bd.vehicle.add(b.vehicle)
        bd.save()

@shared_task
def set_ongoing(bookingObj):
    b = booking.objects.get(bookingId=bookingObj['bookingId'])
    b.status = STATUS_TYPE_CHOICES[2][0]
    b.save()

@shared_task
def set_completed(bookingObj):
    b = booking.objects.get(bookingId=bookingObj['bookingId'])
    b.status = STATUS_TYPE_CHOICES[3][0]
    b.save()

@shared_task
def cancel_after_one_hour(bookingObj):
    b = booking.objects.get(bookingId=bookingObj['bookingId'])
    if b.status != STATUS_TYPE_CHOICES[1][0]:
        b.status = STATUS_TYPE_CHOICES[4][0]
        make_available(b)
        b.save()

@shared_task
def send_notification_and_location(bookingObj):
    b = booking.objects.get(bookingId=bookingObj['bookingId'])
    if b.status == STATUS_TYPE_CHOICES[1][0]:
        #send mail
        content = {
            'bookingID': b.bookingId,
            'lat': b.vehicle.address.lat,
            'lon': b.vehicle.address.lon,
            'carMakeModel': str(b.vehicle.maker)+', '+str(b.vehicle.model),
        }
        t = Thread(target=send_reminder, kwargs={'email': b.vehicle.owner.email, 'content': content})
        t.start()
        content = {
            'bookingID': b.bookingId,
            'lat': b.vehicle.address.lat,
            'lon': b.vehicle.address.lon,
            'carMakeModel': str(b.vehicle.maker)+', '+str(b.vehicle.model),
        }
        t = Thread(target=send_reminder, kwargs={'email': b.customer.email, 'content': content})
        t.start()
        #send sms
        o = profile.objects.get(user=b.vehicle.owner)
        c = profile.objects.get(user=b.customer)
        t = Thread(target=send_reminder_sms_to_customer, kwargs={'phoneNumber': c.mobile, 'customerName': b.customer.first_name, 'bookingId': b.bookingId, 'ownerMobile': o.mobile, 'loc': (b.vehicle.address.lat,b.vehicle.address.lon)})
        t.start()
