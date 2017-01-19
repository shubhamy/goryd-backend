from django.conf.urls import include, url
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'coupons' , CouponViewSet , base_name ='coupons')
router.register(r'payment' , paymentViewSet , base_name ='payment')

urlpatterns = [
    url(r'^', include(router.urls)),
    ]
