from django.http import *
from django.contrib.auth.decorators import login_required
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from datetime import datetime
from calendar import timegm
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from users.models import profile
from rest_framework.response import Response
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework.test import APIClient
from rest_framework.exceptions import *
from requests import request, ConnectionError
from django.core.files.base import ContentFile
from users.models import *
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import permissions
from django.http import HttpResponse
from django.shortcuts import render

@csrf_exempt
@api_view(['PUT', 'POST'])
def obtain_goryd_token(request):
    client = APIClient()
    error_message = {"non_field_errors": ["Unable to login with provided credentials."]}
    if all(i in request.data for i in ['username', 'password']):
        try:
            # to login with username and password
            if User.objects.filter(username=request.data['username']).exists():
                try:
                    response = client.post('/api/alt-token-auth/', request.data)
                    return response
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)
            # to login with mobile and password
            elif profile.objects.filter(mobile=request.data['username']).exists():
                p = profile.objects.get(mobile=request.data['username'])
                u = p.user
                request.data['username'] = u.username
                try:
                    response = client.post('/api/alt-token-auth/', request.data)
                    return response
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data=error_message)

def create_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    # Include original issued at time for a brand new token, to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(datetime.datetime.utcnow().utctimetuple())
    return jwt_encode_handler(payload)

# @api_view(['GET'])
# @permission_classes((permissions.IsAuthenticated,))
# def afterLogin(request):
#     if request.GET['mode'] == 'validate':
#         return Response(status=status.HTTP_200_OK, data={'action': 'validate', 'token': create_token(request.user)})
#     elif request.GET['mode'] == 'login':
#         return Response(status=status.HTTP_200_OK, data={'action': 'login', 'token': create_token(request.user)})
#     else:
#         return Response(status=status.HTTP_400_BAD_REQUEST)
