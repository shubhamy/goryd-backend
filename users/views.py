from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import json
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from API.permissions import *
from .serializers import *
import random
from support.sendSmsApi import *
from support.sendMailApi import *
from threading import Thread
from backend import settings
from API.views import create_token
import datetime
from multiprocessing import Pool

@csrf_exempt
def logoutView(request):
    logout(request)
    data = {'status' : 200}
    return HttpResponse(json.dumps(data), content_type='application/json')

def sendOTP(user):
    OTP = random.randint(100000, 999999)
    p = profile.objects.get(user=user)
    p.otp = OTP
    p.save()
    send_otp(p.mobile, OTP)

def getDetails(request, mobile, dob):
    template_name = 'form.html'
    backend = request.session['partial_pipeline']['backend']
    return render(request, template_name, {'backend': backend, 'mobile': mobile})

@csrf_exempt
@api_view(['POST'])
def validateOTP(request):
    if request.path == '/register/validateOTP/':
        #register
        p = profile.objects.filter(pk=int(request.data['pk'])).first()
        if p.otp == int(request.data['otp']) and p.otp is not None:
            p.otp = None
            p.isMobileVerified = True
            p.user.save()
            p.save()
            content = {'name': p.user.first_name}
            t = Thread(target=send_on_registration, kwargs={'email': p.user.email, 'content': content, 'email_templates': 'registration-renter.html'})
            t.start()
            return Response(status=status.HTTP_200_OK, data={'token': create_token(p.user)})
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={'error': 'Incorrect OTP'})
    elif request.path == '/forgotPassword/validateOTP/':
        #forgot password
        p = profile.objects.filter(pk=request.data['pk']).first()
        if p.otp == int(request.data['otp']) and p.otp is not None:
            p.otp = None
            p.save()
            return Response(status=status.HTTP_200_OK, data={'token': create_token(p.user)})
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={'error': 'Incorrect OTP'})

class registerView(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def post(self , request ):
        data = {'status' : 'default' , 'message' : '' }
    	name = request.data['name'].split(" ")
    	email = request.data['email']
        password = request.data['password']
    	mobile = request.data['mobile']
        dob = request.data['dob']
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Email id already exists.Please login!"})
        elif profile.objects.filter(mobile=mobile):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Mobile number already exists.Please login!"})
        else:
            user = User.objects.create(username = email)
            user.first_name = name[0]
            try:
                user.last_name = name[1]
            except:
                user.last_name = ''
            user.email = email
            user.set_password(password)
            user.is_active = False
            p = profile(user = user)
            p.mobile = mobile
            try:
                p.dob = datetime.datetime.strptime(dob, '%d-%m-%Y')
            except:
                raise ValidationError({"error": "Incorrect date of birth"})
            try:
                user.is_active = True
                user.save()
                p.save()
                pool = Pool(processes=1)
                r = pool.apply_async(sendOTP, [user])
                return Response(data={'pk': p.pk}, status=status.HTTP_200_OK)
            except:
                user.delete()
                p.delete()
                return Response(status=status.HTTP_502_BAD_GATEWAY, data={'error': "Something goes wrong on our side. Please try again!"})

class ForgotPassword(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        if 'mobile' in request.data:
            p = profile.objects.filter(mobile=int(request.data['mobile'])).first()
        elif 'pk' in request.data:
            p = profile.objects.filter(pk=int(request.data['pk'])).first()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': "You shall not pass"})
        try:
            sendOTP(p.user)
            return Response(status=status.HTTP_200_OK, data={'pk': p.pk})
        except:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': "User does not exist"})

class NewPassword(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        u = request.user
        try:
            u.set_password(request.data['password'])
            u.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': "specify the password"})

class userReviewCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated , )
    queryset = userReviewComment.objects.all()
    serializer_class = userReviewCommentSerializer

class profileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = profileSerializer
    queryset = profile.objects.all()
    def list(self,request):
        u = request.user
        if 'mode' in request.GET:
            token = None
            if self.request.GET['mode'] == 'self':
                print request.user, request.auth
                if request.user != None and request.auth == None:
                    token = create_token(u)
                cp = profile.objects.get(user = u)
                serializedCp = profileSerializer(cp).data
                for i in range(0, len(serializedCp['myReviews'])):
                    email = serializedCp['myReviews'][i]['reviewer']['email']
                    p = profile.objects.get(user=User.objects.get(email=email))
                    serializedCp['myReviews'][i]['reviewer']['dp'] = profileSerializer(p).data['dp']
                serializedCp['token'] = token
                return Response(serializedCp)
            elif self.request.GET['mode'] == 'myrenter':
                cEmail = request.GET['customer']
                c = User.objects.filter(email=cEmail)
                if c.exists():
                    requestedBookingMatch = booking.objects.filter(vehicle__owner=u, status='requested', customer=c)
                    approvedBookingMatch = booking.objects.filter(vehicle__owner=u, status='approved', customer=c)
                    ongoingBookingMatch = booking.objects.filter(vehicle__owner=u, status='ongoing', customer=c)
                    if requestedBookingMatch.exists() or approvedBookingMatch.exists() or ongoingBookingMatch.exists():
                        cp = profile.objects.get(user = c)
                        serializedCp = profileSerializer(cp).data
                        for i in range(0, len(serializedCp['myReviews'])):
                            email = serializedCp['myReviews'][i]['reviewer']['email']
                            p = profile.objects.get(user=User.objects.get(email=email))
                            serializedCp['myReviews'][i]['reviewer']['dp'] = profileSerializer(p).data['dp']
                        # Hiding mobile number, isOwner status, dl and idproof for requested bookings
                        if requestedBookingMatch.exists() and not (approvedBookingMatch.exists() or ongoingBookingMatch.exists()):
                            serializedCp.pop('dl')
                            serializedCp.pop('mobile')
                            serializedCp.pop('isOwner')
                            serializedCp.pop('idProof')
                        return Response(serializedCp)
                    else:
                        return Response(status=status.HTTP_401_UNAUTHORIZED, data={'error': "Sorry! Only profiles who have requested your cars are visible to you."})
                else:
                    raise ValidationError("Inappropriate email id provided.")
            else:
                raise ValidationError("Unidentified objects")
        else:
            raise ValidationError("missing parameters")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.user:
            if 'dp' in request.data:
                instance.dp = request.data['dp']
                instance.save()
                return Response(status=status.HTTP_200_OK)
            elif 'dl' in request.data:
                instance.dl = request.data['dl']
                instance.isVerifiedRenter = False
                instance.save()
                return Response(status=status.HTTP_200_OK, data={'content': 'Thanks! We will verify your Driver License shortly.'})
            elif 'idProof' in request.data:
                instance.idProof = request.data['idProof']
                instance.isVerifiedRenter = False
                instance.save()
                return Response(status=status.HTTP_200_OK, data={'content': 'Thanks! We will verify your Identity Proof shortly.'})
            elif all(i in request.data for i in ['mobile', 'first_name', 'last_name']):
                instance.mobile = request.data['mobile']
                instance.save()
                u = instance.user
                u.first_name = request.data['first_name']
                u.last_name = request.data['last_name']
                u.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "I don't like your request parameters"})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Invalid credentials for this request")
