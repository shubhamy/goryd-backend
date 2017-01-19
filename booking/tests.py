from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .views import bookingViewSet
from listing.models import vehicle
from .models import *
from listing.fixtures import *
from users.fixtures import *
import datetime
from django.utils import timezone


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microsecond)

class BookingTest(APITestCase):
    
    fixtures = ['auth_user_data.json', 'user_data.json', 'listing_data.json']
    
    def setUp(self):
        self.client = APIClient()
        self.anyRandomUser = User.objects.create(username="random", email="test@test.com", password="random")
        self.client.force_login(user=self.anyRandomUser)
        self.requestFactory = APIRequestFactory(enforce_csrf_check=True)
        
    def tearDown(self):
        self.client.logout()

    def test_booking_viewset(self):
        auth_request = self.requestFactory.get('/api/booking/mybooking/')
        auth_request.user = self.anyRandomUser
        
        unauth_request = self.requestFactory.get('/api/booking/mybooking/')
        
        auth_resp = bookingViewSet.as_view({'get': 'list'})(auth_request)
        unauth_resp = bookingViewSet.as_view({'get': 'list'})(unauth_request)
        
        ## Only authorized users are allowed
        self.assertEqual(auth_resp.status_code, 200)
        self.assertEqual(unauth_resp.status_code, 403)


class BookingAddTest(BookingTest):
    
    def test_booking_params(self):
        '''
        try:
            vehicleId = vehicle.objects.all()[0].pk
        except:
            pass
        '''
        pick = datetime.datetime.now() + datetime.timedelta(1,0)
        drop = datetime.datetime.now() + datetime.timedelta(1,20)
        data = {"vehicle": 1, "pickupTime": pick.strftime('%Y-%m-%dT%H:%M:%S%z'), "dropTime": drop.strftime('%Y-%m-%dT%H:%M:%S%z')}
        
        #valid query params
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=1', data=data)
        self.assertEqual(auth_resp.status_code, 201)
        ##new booking added
        b = booking.objects.get()
        self.assertEqual(b.pickupTime, timezone.make_aware(chop_microseconds(pick), timezone.get_default_timezone()))
        self.assertEqual(b.dropTime, timezone.make_aware(chop_microseconds(drop), timezone.get_default_timezone()))
        self.assertEqual(b.bookingId, str(1))
        self.assertEqual(b.vehicle.pk, 1)
        
        #invalid mode
        auth_resp = self.client.post('/api/booking/mybooking/?mode=abc&id=1', data=data)
        self.assertEqual(auth_resp.status_code, 400)

        #missing mode
        auth_resp = self.client.post('/api/booking/mybooking/?mode=&id=1', data=data)
        self.assertEqual(auth_resp.status_code, 400)

        #missing id
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=', data=data)
        self.assertEqual(auth_resp.status_code, 400)
        
    def test_booking_body(self):
        '''
        try:
            vehicleId = vehicle.objects.all()[0].pk
        except:
            pass
        '''
        vehicleId = 1
        pick = datetime.datetime.now() + datetime.timedelta(1,0)
        drop = datetime.datetime.now() + datetime.timedelta(1,20)
        data_correct = {"vehicle": vehicleId, "pickupTime": pick.strftime('%Y-%m-%dT%H:%M:%S%z'), "dropTime": drop.strftime('%Y-%m-%dT%H:%M:%S%z')}
        
        temp = data_correct.copy()
        temp['vehicle'] = ''
        data_missing_vehicle = temp.copy() #1
        temp['vehicle'] = vehicleId
        temp['pickupTime'] = ''
        data_missing_pickupTime = temp.copy() #2
        temp['pickupTime'] = pick
        temp['dropTime'] = ''
        data_missing_dropTime = temp.copy() #3
        temp['dropTime'] = drop
        
        temp['vehicle'] = 'dsffsdf'
        data_incorrect_vehicle = temp.copy() #4
        temp['vehicle'] = vehicleId
        temp['pickupTime'] = pick - datetime.timedelta(2,0)
        data_incorrect_pickupTime = temp.copy() #5
        temp['pickupTime'] = pick
        temp['dropTime'] = drop - datetime.timedelta(2,20)
        data_incorrect_dropTime = temp.copy() #6
        temp['dropTime'] = drop
        
        temp['dropTime'] = pick
        temp['pickTime'] = drop
        data_incorrect_datetime = temp.copy() #7
        temp['dropTime'] = drop
        temp['pickTime'] = pick
        
        ##performing tests
        #1
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_missing_vehicle)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #2
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_missing_pickupTime)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #3
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_missing_dropTime)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #4
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_incorrect_vehicle)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #5
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_incorrect_pickupTime)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #6
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_incorrect_dropTime)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
        #7
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id=2', data=data_incorrect_datetime)
        self.assertEqual(auth_resp.status_code, 400)
        print auth_resp.data
        
class BookingUpdateTest(BookingTest):
    
    def addBooking(self, bid=1):
        '''
        try:
            vehicleId = vehicle.objects.all()[0].pk
        except:
            pass
        '''
        vehicleId = 1
        pick = datetime.datetime.now() + datetime.timedelta(1,0)
        drop = datetime.datetime.now() + datetime.timedelta(1,20)
        data = {"vehicle": vehicleId, "pickupTime": pick.strftime('%Y-%m-%dT%H:%M:%S%z'), "dropTime": drop.strftime('%Y-%m-%dT%H:%M:%S%z')}
        auth_resp = self.client.post('/api/booking/mybooking/?mode=new&id='+str(bid), data=data)
        self.assertEqual(auth_resp.status_code, 201)
    
    def test_booking_update_params(self):
        '''
        try:
            vehicleId = vehicle.objects.all()[1].pk
        except:
            pass
        '''
        vehicleId = 2
        pick = datetime.datetime.now() + datetime.timedelta(1,0)
        drop = datetime.datetime.now() + datetime.timedelta(1,20)
        data = {"vehicle": vehicleId, "pickupTime": pick.strftime('%Y-%m-%dT%H:%M:%S%z'), "dropTime": drop.strftime('%Y-%m-%dT%H:%M:%S%z')}
        
        self.addBooking()
        
        #not found
        auth_resp = self.client.put('/api/booking/mybooking/10000000/?mode=abc&id=20', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 404)
        
        #invalid instance
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=abc&id=20', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)
        
        #invalid mode
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=abc&id=1', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)

        #missing mode
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=&id=1', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)

        #missing id
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=update&id=', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)
        
        #valid query params
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=update&id=1', data=data)
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 200)
        b = booking.objects.get(active=True)
        self.assertEqual(b.pickupTime, timezone.make_aware(chop_microseconds(pick), timezone.get_default_timezone()))
        self.assertEqual(b.dropTime, timezone.make_aware(chop_microseconds(drop), timezone.get_default_timezone()))
        self.assertEqual(b.bookingId, str(1))
        self.assertEqual(b.vehicle.pk, vehicleId)
        
    def test_booking_cancel_params(self):
        self.addBooking()
        
        #not found
        auth_resp = self.client.put('/api/booking/mybooking/21000000000/?mode=abc&id=20')
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 404)
        
        #invalid mode
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=abc&id=1')
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)

        #missing mode
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=&id=1')
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)

        #missing id
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=update&id=')
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)
        
        #valid query params
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=cancel&id=1')
        #print auth_resp.data
        self.assertEqual(auth_resp.status_code, 200)
        b = booking.objects.get(active=False)
        self.assertEqual(b.bookingId, str(1))
        self.assertEqual(b.pk, 1)
        
    def test_booking_user_match(self):
        self.addBooking()
        
        ##changing user
        self.client.logout()
        u = User.objects.create(username="newrandomuser", email="test@test.com", password="random")
        self.client.force_login(user=u)
        ##user changed
        
        #valid query params
        auth_resp = self.client.put('/api/booking/mybooking/1/?mode=cancel&id=1')
        print auth_resp.data
        self.assertEqual(auth_resp.status_code, 400)