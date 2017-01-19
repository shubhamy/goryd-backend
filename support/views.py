from django.shortcuts import render
from rest_framework import viewsets , permissions , serializers, status
from rest_framework.permissions import *
from rest_framework.exceptions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from django.core import serializers
from django.http import JsonResponse
from API.permissions import *
from .models import *
from .serializers import *
from django.http import HttpResponse

# Create your views here.
class feedbackViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = feedbackSerializer
    def get_queryset(self):
        u = self.request.user
        return feedback.objects.all()

class ticketViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ticketFormSerializer
    def get_queryset(self):
        return ticket.objects.filter(user=self.request.user)
    def list(self, request, *args, **kwargs):
        if 'category' in request.query_params:
            categoryChoices = []
            for i in SubcategorySerializer(Subcategory.objects.all(), many=True).data:
                categoryChoices.append(i["name"])
            return Response(categoryChoices)

class faqViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = faqSerializer
    def get_queryset(self):
        return faq.objects.all()

class subscriberViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = subscriberSerializer
    def get_queryset(self):
        return subscriber.objects.all()

class UserQueryViewSet(viewsets.ModelViewSet):
    serializer_class = UserQuerySerializer