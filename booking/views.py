from rest_framework import viewsets , permissions, status
from rest_framework.exceptions import *
from rest_framework.response import Response
from API.permissions import *
from .serializers import *
import datetime
from threading import Thread
from listing.serializers import *
from support.sendMailApi import *
from support.sendSmsApi import *
from .tasks import set_ongoing, set_completed, make_available
from django.conf import settings

class bookingViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = bookingSerializer
    def list(self, request):
        u = request.user
        if 'status' in request.GET:
            try:
                status = request.GET['status']
            except:
                status = ''
            if status:
                serializedBookings = bookingSerializer(booking.objects.filter(customer=u, status=status), many=True).data
                if status==STATUS_TYPE_CHOICES[1][0]:
                    for i in range(0, len(serializedBookings)):
                        v = vehicle.objects.get(pk=serializedBookings[i]['vehicle'])
                        serializedBookings[i]['pickupAddress'] = addressSerializer(v.address).data
            else:
                serializedBookings = bookingSerializer(booking.objects.filter(customer=u), many=True).data
        if 'pk' in request.GET:
            pk = request.GET['pk']
            serializedBookings = bookingSerializer(booking.objects.filter(pk=pk), many=True).data
        for sb in range(0, len(serializedBookings)):
            vd = vehicleSerializer(vehicle.objects.get(pk=serializedBookings[sb]['vehicle'])).data
            serializedBookings[sb]['vehicle'] =  {
                "pk": vd['id'],
                "regNum": vd['regNum'],
                "rating": vd['rating'],
                "year": vd['year'],
                "kms": vd['kms'],
                "gearType": vd['gearType'],
                "deposit": vd['deposit'],
                "active": vd['active'],
                "model": ModelSerializer(Model.objects.get(pk=vd['model'])).data['model'],
                "maker": MakerSerializer(Maker.objects.get(pk=vd['maker'])).data['maker'],
                "media": MediaSerializer(Media.objects.filter(vehicle=vehicle.objects.get(pk=vd['id'])), many=True).data
            }
            cd = profileSerializer(User.objects.get(pk=serializedBookings[sb]['customer']).ecommerceProfile).data
            serializedBookings[sb]['customer'] = {
                "first_name": cd['user']['first_name'],
                "last_name": cd['user']['last_name'],
                "dp": cd['dp']
            }
            images = []
            for image in serializedBookings[sb]['vehicle']['media']:
                images.append(image['attachment'])
            serializedBookings[sb]['vehicle']['media'] = images
        return Response(serializedBookings)

    def update(self, request, *args, **kwargs):
        instance = booking.objects.get(pk=kwargs['pk'])
        u = request.user
        data = request.data
        if u == instance.customer:
            # cancelled
            if data['status'] == STATUS_TYPE_CHOICES[4][0] and (instance.status == STATUS_TYPE_CHOICES[0][0] or instance.status == STATUS_TYPE_CHOICES[1][0]):
                instance.status = STATUS_TYPE_CHOICES[4][0]
                make_available(instance)
                try:
                    content = ''
                    t = Thread(target=send_on_cancel_booking, kwargs={'email': instance.customer.email, 'content': content, 'email_templates': 'booking-cancelled-renter.html'})
                    t.start()
                    content = ''
                    t = Thread(target=send_on_cancel_booking, kwargs={'email': instance.vehicle.owner.email, 'content': content, 'email_templates': 'booking-cancelled-owner.html'})
                    t.start()
                except:
                    pass
                instance.save()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Not Allowed'})
        elif u == instance.vehicle.owner:
            if data['status'] == STATUS_TYPE_CHOICES[5][0] and instance.status == STATUS_TYPE_CHOICES[0][0]:
                # rejected
                instance.status = STATUS_TYPE_CHOICES[5][0]
                instance.ownerComment = data['comment']
                make_available(instance)
                try:
                    content = {
                        'name': instance.customer.first_name,
                        'bookingID': instance.bookingId,
                        'fromDateTime': str(instance.pickupTime),
                        'toDateTime': str(instance.dropTime),
                        'bookingDate': str(datetime.datetime.now().date()),
                        'status': instance.status,
                        'carMakeModel': str(instance.vehicle.maker)+', '+str(instance.vehicle.model),
                    }
                    t = Thread(target=send_on_reject_booking, kwargs={'email': instance.customer.email, 'content': content, 'email_templates': 'booking-rejected-renter.html'})
                    t.start()
                    content = {
                        'name': instance.vehicle.owner.first_name,
                        'renterName': instance.customer.first_name+' '+instance.customer.last_name,
                        'bookingID': instance.bookingId,
                        'fromDateTime': str(instance.pickupTime),
                        'toDateTime': str(instance.dropTime),
                        'bookingDate': str(datetime.datetime.now().date()),
                        'status': instance.status,
                        'carMakeModel': str(instance.vehicle.maker)+', '+str(instance.vehicle.model),
                    }
                    t = Thread(target=send_on_reject_booking, kwargs={'email': instance.vehicle.owner.email, 'content': content, 'email_templates': 'booking-rejected-owner.html'})
                    t.start()
                except Exception, e:
                    print e
                instance.save()
            elif data['status'] == STATUS_TYPE_CHOICES[1][0]: #and instance.status == STATUS_TYPE_CHOICES[0][0]:
                # approved
                instance.status = STATUS_TYPE_CHOICES[1][0]
                try:
                    content = {
                        'name': instance.customer.first_name,
                        'bookingID': instance.bookingId,
                        'fromDateTime': str(instance.pickupTime),
                        'toDateTime': str(instance.dropTime),
                        'bookingDate': str(datetime.datetime.now().date()),
                        'status': instance.status,
                        'carMakeModel': str(instance.vehicle.maker)+', '+str(instance.vehicle.model),
                        'totalRent': instance.totalCost,
                        'deposit': instance.vehicle.deposit,
                        'pickupLoc': instance.pickupLoc,
                    }
                    t = Thread(target=send_on_confirmed_booking, kwargs={'email': instance.customer.email, 'content': content, 'email_templates': 'booking-confirmed-renter.html'})
                    t.start()
                    t = Thread(target=send_on_booking_approval(instance.customer.ecommerceProfile.mobile, instance.customer.first_name, instance.bookingId, str(instance.pickupTime.date()), str(instance.pickupTime.minute)+":"+str(instance.pickupTime.second), str(instance.dropTime), str(instance.dropTime.minute)+":"+str(instance.dropTime.second), str(instance.vehicle.maker)+', '+str(instance.vehicle.model), instance.totalCost, 'cash on delivery', 'http://maps.google.com'))
                    t.start()
                    content = {
                        'name': instance.vehicle.owner.first_name,
                        'renterName': instance.customer.first_name+' '+instance.customer.last_name,
                        'bookingID': instance.bookingId,
                        'fromDateTime': str(instance.pickupTime),
                        'toDateTime': str(instance.dropTime),
                        'bookingDate': str(datetime.datetime.now().date()),
                        'status': instance.status,
                        'carMakeModel': str(instance.vehicle.maker)+', '+str(instance.vehicle.model),
                        'totalRent': instance.totalCost,
                        'deposit': '',
                        'pickupLoc': instance.pickupLoc,
                    }
                    t = Thread(target=send_on_confirmed_booking, kwargs={'email': instance.vehicle.owner.email, 'content': content, 'email_templates': 'booking-confirmed-owner.html'})
                    t.start()
                except Exception, e:
                    print e
                instance.save()
                # zone = pytz.timezone(settings.TIME_ZONE)
                set_ongoing.apply_async((bookingSerializer(instance).data,), eta=instance.pickupTime, expires=instance.pickupTime + datetime.timedelta(seconds=120))
                set_completed.apply_async((bookingSerializer(instance).data,), eta=instance.dropTime, expires=instance.dropTime + datetime.timedelta(seconds=120))
            elif data['status'] == STATUS_TYPE_CHOICES[3][0] and instance.status == STATUS_TYPE_CHOICES[1][0]:
            # elif data['status'] == STATUS_TYPE_CHOICES[3][0] and instance.status == STATUS_TYPE_CHOICES[2][0]:
                # completed
                instance.status =STATUS_TYPE_CHOICES[3][0]
                instance.vehicle.totalBookings += 1
                instance.vehicle.totalEarning += instance.totalCost
                instance.vehicle.save()
                instance.save()
                # implement
                #send mail
            else:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Not Allowed'})
        else:
            return Response(status=status.HTTP_403_UNAUTHORIZED, data={'error': 'Not Authorized'})
        return Response(data=bookingSerializer(instance).data, status=status.HTTP_200_OK)

class bookingsPhotosViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = bookingsPhotosSerializer
    queryset = bookingsPhoto.objects.all()

class bookingReviewsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    def list(self, request):
        u = request.user
        if request.query_params['checkPastBookings'] == 'true':
            #as a customer is given more priority over being as an owner
            lastBookingAsCustomer = booking.objects.filter(comment=None, customer=u, status=STATUS_TYPE_CHOICES[3][0])
            lastBookingAsowner = booking.objects.filter(userReview=None, vehicle__owner=u, status=STATUS_TYPE_CHOICES[3][0])
            if lastBookingAsCustomer.exists():
                dataToSend = {
                    "pk": lastBookingAsCustomer.last().pk,
                    "flag": "customer"
                }
                return Response(dataToSend)
            elif lastBookingAsowner.exists():
                dataToSend = {
                    "pk": lastBookingAsowner.last().pk,
                    "flag": "owner"
                }
                return Response(dataToSend)
            else:
                return Response(status=status.HTTP_200_OK, data={"details": "No un-rated past bookings."})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    def update(self, request, *args, **kwargs):
        b = booking.objects.get(pk=kwargs['pk'])
        if request.user == b.customer:
            vr = vehicleReviewComment.objects.create(text=request.data['comment'], rating=request.data['rating'], reviewer=b.customer, vehicle=b.vehicle)
            b.comment = vr
            if b.vehicle.totalBookings ==0:
                b.vehicle.rating = request.data['rating']
            else:
                rating = ((b.vehicle.totalBookings-1)*b.vehicle.rating + request.data['rating'])/(float(b.vehicle.totalBookings))
                b.vehicle.rating - float(format(rating, '.1f'))
            b.save()
            b.vehicle.save()
            vr.save()
            return Response(status=status.HTTP_200_OK)
        elif request.user == b.vehicle.owner:
            ur = userReviewComment.objects.create(text=request.data['comment'], rating=request.data['rating'], reviewer=b.vehicle.owner, profile=b.customer.ecommerceProfile)
            b.userReview = ur
            totalCustomerBooking = len(booking.objects.filter(customer=b.customer, status=STATUS_TYPE_CHOICES[3][0]))
            rating = ((totalCustomerBooking-1)*b.customer.ecommerceProfile.rating + request.data['rating'])/float(totalCustomerBooking)
            b.customer.ecommerceProfile.rating = float(format(rating, '.1f'))
            b.save()
            print b.customer.ecommerceProfile.pk
            b.customer.ecommerceProfile.save()
            ur.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
