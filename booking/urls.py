from django.conf.urls import include, url
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'mybooking' , bookingViewSet , base_name ='booking')
router.register(r'review', bookingReviewsViewSet, base_name='bookingReview')

urlpatterns = [
    url(r'^', include(router.urls)),
]
