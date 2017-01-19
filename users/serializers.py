from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from rest_framework.response import Response

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", 'last_name', 'email']

class userReviewCommentSerializer(serializers.ModelSerializer):
    reviewer = userSerializer(read_only=True, many=False)
    class Meta:
        model = userReviewComment
        fields = ['reviewer', 'rating', 'text']

class profileSerializer(serializers.ModelSerializer):
    user = userSerializer(many = False , read_only = True)
    myReviews = userReviewCommentSerializer(many = True , read_only = True)
    class Meta:
        model = profile
        fields = ['pk', 'user', 'myReviews', 'rating', 'mobile', 'dob', 'dp', 'dl', 'idProof', 'aboutMe','isOwner', 'isVerifiedRenter']
