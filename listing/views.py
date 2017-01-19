from rest_framework import viewsets , permissions , serializers
from rest_framework.exceptions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from url_filter.integrations.drf import DjangoFilterBackend
from django.core import serializers
from django.http import JsonResponse
from API.permissions import *
from .serializers import *
from booking.models import booking
from booking.serializers import bookingSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import json, random
import datetime
from finance.views import *
from getSearchResults import *
from django.db.models import Q
import os

class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = addressSerializer
    def get_queryset(self):
        u = self.request.user
        return Address.objects.all()

class mediaView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def post(self, request):
        u = request.user
        v = get_object_or_404(vehicle, pk=request.data['vehicle'])

        # running loop (l-1)/2 times where l is the length of request.data. it has one vehicle key and equal numbers of attachment and name keys. Hence divided by 2. On every loop, it creates a media object with an attachment and a name.
        # Request.data -> <QueryDict: {u'attachment[2]': [<InMemoryUploadedFile: ha1.jpg (image/jpeg)>], u'name[1]': [u'normal'], u'name[0]': [u'dp'], u'name[2]': [u'normal'], u'attachment[0]': [<InMemoryUploadedFile: ha3.jpg (image/jpeg)>], u'vehicle': [u'80'], u'attachment[1]': [<InMemoryUploadedFile: ha2.jpg (image/jpeg)>]}>
        if len(request.data)<3:
            return Response(status=status.HTTP_200_OK, data={'error': 'No image given.'})
        else:
            for i in range(0, (len(request.data)-1)/2):
                name = 'name['+str(i)+']'
                attachment = 'attachment['+str(i)+']'
                existedMedia = Media.objects.filter(user=u, vehicle=v, name=request.data[name])
                if len(existedMedia)<5 and request.data[name] == 'normal':
                    media = Media.objects.create(user=u, vehicle=v, name=request.data[name], attachment=request.FILES[attachment])
                    media.save()
                elif len(existedMedia)<1 and request.data[name] == 'dp':
                    media = Media.objects.create(user=u, vehicle=v, name=request.data[name], attachment=request.FILES[attachment])
                    media.save()
                else:
                    existedMedia.first().delete()
                    media = Media.objects.create(user=u, vehicle=v, name=request.data[name], attachment=request.FILES[attachment])
                    media.save()

            return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = Media.objects.get(pk=request.query_params['pk'])
        if instance.user == request.user:
            name = os.path.join(settings.BASE_DIR,'media_root',instance.attachment.name)
            instance.delete()
            try:
                os.remove(os.path.abspath(name))
            except Exception, e:
                print e
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={'error': "You're not authorized for this operation"})

    def put(self, request, *args, **kwargs):
        instance = Media.objects.get(pk=kwargs['pk'])
        instance.name = request.data['name']
        instance.save()
        return Response(status=status.HTTP_200_OK)

class MakerViewSet(viewsets.ModelViewSet):
    permission_classes = (isAdminOrReadOnly, )
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['maker']

class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = (isAdminOrReadOnly, )
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['model', 'maker']
    def get_queryset(self):
        param = self.request.query_params['car']
        try:
            maker = param.split(' ')[0]
            model = param.split(' ')[1]
            return Model.objects.filter(Q(maker__maker__contains=maker) & Q(model__contains=model))
        except:
            model = maker
            return Model.objects.filter(Q(maker__maker__contains=maker) | Q(model__contains=model))

class vehicleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = vehicleSerializer
    queryset = vehicle.objects.all()
    def list(self, request):
        if 'pk' in request.query_params:
            try:
                v = vehicle.objects.filter(pk=request.query_params['pk'], owner=request.user)
                vehicleData = vehicleSerializer(v, many=True).data[0]
                a = addressSerializer(Address.objects.filter(pk=vehicleData['address']), many=True).data[0]
                model = get_object_or_404(Model, pk=vehicleData['model'])
                aval = v[0].availabilities.all()
                availSerial = availabilitySerializer(aval, many=True).data
                datesList = []
                for date in availSerial:
                    datesList.append(date['date'])
                dataToSend = {
                    "pk": vehicleData['id'],
                    "model": ModelSerializer(model).data['model'],
                    "maker": ModelSerializer(model).data['maker']['maker'],
                    "year": vehicleData['year'],
                    "kms": vehicleData['kms'],
                    "gearType": vehicleData['gearType'],
                    "address": a,
                    "availabilities": datesList,
                    "media": MediaSerializer(v[0].photos.all().order_by('name'), many=True).data,
                    "weekdayPrice": vehicleData['weekdayPrice'],
                    "weekendPrice": vehicleData['weekendPrice'],
                    "deposit": vehicleData['deposit'],
                    "rating": vehicleData['rating'],
                    "isActive": vehicleData['active'],
                    "isVerified": vehicleData['verified'],
                    "regNum": vehicleData['regNum']
                }
                return Response(dataToSend)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
        elif 'status' in request.query_params:
            vs = vehicle.objects.filter(owner=request.user)
            requiredBookings = []
            for v in vs:
                b = booking.objects.filter(vehicle=v, status=request.query_params['status'])
                requiredBookings += (bookingSerializer(b, many=True).data)
            for rb in range(0, len(requiredBookings)):
                vd = vehicleSerializer(vehicle.objects.get(pk=requiredBookings[rb]['vehicle'])).data
                requiredBookings[rb]['vehicle'] = {
                    "pk": vd['id'],
                    "regNum": vd['regNum'],
                    "year": vd['year'],
                    "rating": vd['rating'],
                    "totalBookings": vd['totalBookings'],
                    "kms": vd['kms'],
                    "gearType": vd['gearType'],
                    "deposit": vd['deposit'],
                    "active": vd['active'],
                    "model": ModelSerializer(Model.objects.get(pk=vd['model'])).data['model'],
                    "maker": MakerSerializer(Maker.objects.get(pk=vd['maker'])).data['maker'],
                    "media": MediaSerializer(Media.objects.filter(vehicle=vehicle.objects.get(pk=vd['id'])), many=True).data
                }
                images = []
                for image in requiredBookings[rb]['vehicle']['media']:
                    images.append(image['attachment'])
                requiredBookings[rb]['vehicle']['media'] = images
                requiredBookings[rb]['customer'] = userSerializer(booking.objects.get(bookingId=requiredBookings[rb]['bookingId']).customer).data

                p = profile.objects.get(user=User.objects.get(email=requiredBookings[rb]['customer']['email']))
                requiredBookings[rb]['customer']['dp'] = profileSerializer(p).data['dp']
                requiredBookings[rb]['customer']['dl'] = profileSerializer(p).data['dl']
                requiredBookings[rb]['customer']['reviews'] = profileSerializer(p).data['myReviews']
                requiredBookings[rb]['customer']['rating'] = profileSerializer(p).data['rating']
                requiredBookings[rb]['customer']['about'] = profileSerializer(p).data['aboutMe']
                requiredBookings[rb]['customer']['isOwner'] = profileSerializer(p).data['isOwner']
                requiredBookings[rb]['customer']['isVerifiedRenter'] = profileSerializer(p).data['isVerifiedRenter']
            return Response(requiredBookings)
        elif 'checkLastListing' in request.query_params:
            if request.query_params['checkLastListing'] == 'true':
                try:
                    v = vehicle.objects.filter(isListingComplete=False, owner=request.user)[0]
                    return Response(v.pk)
                except:
                    return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": 'Incorrect query parameters.'})
        else:
            v = vehicle.objects.filter(owner=request.user)
            serializer = vehicleSerializer(v, many=True)
            for i in range(0, len(serializer.data)):
                ms = get_object_or_404(Model, pk=serializer.data[i]['model'])
                serializer.data[i]['maker'] = ModelSerializer(ms).data['maker']['maker']
                serializer.data[i]['model'] = ModelSerializer(ms).data['model']
                v_temp = get_object_or_404(vehicle, pk=serializer.data[i]['id'])
                md = v_temp.photos.all()
                serializer.data[i]['media'] = MediaSerializer(md.order_by('name'), many=True).data,
            return Response(serializer.data)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner == request.user:
            if 'isListingComplete' in request.data:
                instance.isListingComplete = request.data['isListingComplete']
                instance.active = True
                instance.save()
                p = profile.objects.get(user=request.user)
                p.isOwner = True
                p.save()
                return Response(status=status.HTTP_200_OK)
            elif all(i in request.data for i in ['pk', 'action']):
                try:
                    vMedia = Media.objects.get(vehicle=vehicle.objects.get(pk=instance.pk), pk=request.data['pk'])
                    if request.data["action"] == "delete":
                        vMedia.delete()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unaccepted action'})
                except:
                    raise ValidationError("Either images does not exist or you are not authorized for this action.")
            elif 'active' in request.data:
                instance.active = request.data['active']
                instance.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(data={"error": "I don't understand your intentions"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"error": "Unauthorized user"}, status=status.HTTP_401_UNAUTHORIZED)
    def delete(self, request, *args, **kwargs):
        instance = vehicle.objects.get(pk=request.query_params['pk'])
        if instance.owner == request.user and instance.isListingComplete == False:
            # remove instance from all the availabilities
            for aval in instance.availabilities.all():
                aval.vehicle.remove(instance)
                aval.save()
            # delete all the media for this instance
            for m in instance.photos.all():
                m.delete()
            # finally, delete the instance itself
            instance.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "Unauthorized action."})

class availabilityViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = availabilitySerializer
    def get_queryset(self):
        return None

class vehicleReviewCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = vehicleReviewCommentSerializer
    queryset = vehicleReviewComment.objects.all()

class listingView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        if 'lat' in request.query_params and 'lon' in request.query_params and 'start' in request.query_params and 'end' in request.query_params:
            lat1 = request.query_params['lat']
            lon1 = request.query_params['lon']
            start = request.query_params['start']
            end = request.query_params['end']
            start_datetime = datetime.datetime.strptime(start, '%d-%m-%YT%H:%M')
            end_datetime = datetime.datetime.strptime(end, '%d-%m-%YT%H:%M')

            if start_datetime < end_datetime:
                vehicle_list = filterSearchResults(start_datetime, end_datetime, lat1, lon1)
                if vehicle_list is None:
                    return Response(status=status.HTTP_404_NOT_FOUND, data={'No results found'})
                # creating the data to be sent
                dataToSend = []
                for v,q in vehicle_list.items():
                    d = vehicleSerializer(v).data
                    address = addressSerializer(Address.objects.get(pk=d['address'])).data
                    # areaData = AreaPincodeSerializer(AreaPincode.objects.filter(pincode=int(address['pincode']))[0]).data
                    if not address: #remove this later
                    # if not areaData:
                        address = addressSerializer(Address.objects.get(pk=d['address'])).data #remove this later
                        # address = ''
                    else:
                        # address['street'] = areaData['officeName'] + ' ' + areaData['taluk'] + ' ' + areaData['districtName']
                        # address['state'] = areaData['stateName']
                        # calculating lat and lon
                        r = round(random.uniform(0.00, 0.001),10) # for 1 KM
                        direction = random.randint(0,4)
                        lat2 = address['lat']
                        lon2 = address['lon']
                        if direction == 1:
                            address['lat'] = float(lat2) + r
                            address['lon'] = float(lon2) + r
                        elif direction == 2:
                            address['lat'] = float(lat2) - r
                            address['lon'] = float(lon2) + r
                        elif direction == 3:
                            address['lat'] = float(lat2) - r
                            address['lon'] = float(lon2) - r
                        elif direction == 4:
                            address['lat'] = float(lat2) + r
                            address['lon'] = float(lon2) - r
                    tempData = {
                        "pk": d['id'],
                        "model": ModelSerializer(Model.objects.get(pk=d["model"])).data['model'],
                        "maker": MakerSerializer(Maker.objects.get(pk=d["maker"])).data['maker'],
                        "weekdayPrice": d['weekdayPrice'],
                        "weekendPrice": d['weekendPrice'],
                        "totalCost": calculate_total_rent(d['weekdayPrice'], d['weekendPrice'], start_datetime, end_datetime),
                        "deposit": d['deposit'],
                        "rating": d['rating'],
                        "year": d['year'],
                        "kms": d['kms'],
                        "gearType": d['gearType'],
                        "owner": userSerializer(User.objects.get(pk=d["owner"])).data,
                        "address": address,
                        "media": MediaSerializer(v.photos.all(), many=True).data,
                        "reviews": vehicleReviewCommentSerializer(v.comments.all(), many=True).data,
                        "distance": q[1]
                    }
                    # adding dp to reviewers data
                    for reviews in tempData['reviews']:
                        p = profile.objects.get(user=User.objects.get(email=reviews['reviewer']['email']))
                        reviews['reviewer']['dp'] = profileSerializer(p).data['dp']
                        tempData['reviews'][tempData['reviews'].index(reviews)]['reviewer']['dp'] = reviews['reviewer']['dp']
                    dataToSend.append(tempData)

                return Response(dataToSend)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
