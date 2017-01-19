from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from rest_framework.response import Response
from support.sendMailApi import *
import random, string
from threading import Thread
from .models import CATEGORY_CHOICES

ticketNo = 0

class feedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = feedback
        fields = ('pk','message' , 'rating' , 'user', 'name')
        read_only_fields = ('user',)
    def create(self , validated_data):
        u = self.context['request'].user
        f = feedback(**validated_data)
        if u.is_authenticated():
            f.name = u.get_full_name()
            f.user = u
        f.save()
        return f
    def update(self , instance , validated_data):
        instance.message = validated_data['message']
        return instance

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('name', )

class ticketFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticket
        fields = ('category', 'subject', 'description', 'status')
    def create(self, validated_data):
        global ticketNo
        t = ticket(**validated_data)
        d = self.context['request'].data
        u = self.context['request'].user
        subcat = Subcategory.objects.get(name=d['subcategory'])
        t.user = u
        if ticketNo == 0:
            # check if data is present in the database
            tickets = ticket.objects.all()
            if tickets:
                temp_ticketID = tickets.latest('id')
                ticketNo = int(temp_ticketID.ticketID[3:].split('-')[0])+1
        t.ticketID = 'GR'+str(CATEGORY_CHOICES.index((subcat.category, subcat.category)))+'%03d'%ticketNo+'-'+string.upper(u.username[:2])
        t.category = subcat
        t.description = d['description']
        t.status = d['status']
        content = {'ticket': t.ticketID}
        mailThread = Thread(target=send_on_new_ticket, kwargs={'email': u.email, 'content': content, 'email_templates': 'welcome.html'})
        mailThread.start()
        content = {'ticket': t.ticketID}
        mailThread = Thread(target=send_on_new_ticket, kwargs={'email': "support@goryd.in", 'content': content, 'email_templates': 'welcome.html'})
        mailThread.start()
        ticketNo += 1
        t.save()
        return t


class faqSerializer(serializers.ModelSerializer):
    class Meta:
        model = faq
        fields = ('subject', 'question', 'answer')
        read_only_fields = ('subject', 'question', 'answer')

class subscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = subscriber

    def create(self, validated_data):
        f = subscriber(**validated_data)
        d = self.context['request'].data
        if 'email' in d:
            e = d['email']
            f.email = e
            f.subscribed = True
            f.save()
            return f
        else:
            raise ValidationError(detail= 'Email not found in your request')

class UserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        exclude_fields = ('status')

    def create(self, validated_data):
        q = UserQuery(**validated_data)
        d = self.context['request'].data
        q.email = d['email']
        q.fullname = d['name']
        q.query = d['message']
        q.save()
        content = {
            'IssueId': q.pk,
            'query': q.query,
            'fullname': q.fullname
        }
        t = Thread(target=send_on_new_query, kwargs={'email': q.email, 'content': content, 'email_templates': 'welcome.html'})
        t.start()
        return q
