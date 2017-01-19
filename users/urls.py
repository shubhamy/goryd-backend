from django.conf.urls import include, url
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'profile' , profileViewSet , base_name = 'customerProfile')
router.register(r'userComment' , userReviewCommentViewSet , base_name = 'userComment')
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'mobile/$', getDetails, {'mobile': True, 'dob': True}, name='acquire_mobile_number')
    ]
