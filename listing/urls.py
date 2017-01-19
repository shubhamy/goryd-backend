from django.conf.urls import include, url
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'address' , AddressViewSet , base_name = 'address')
router.register(r'review' , vehicleReviewCommentViewSet , base_name ='review')
router.register(r'maker', MakerViewSet, base_name='makers')
router.register(r'model', ModelViewSet, base_name='models')
router.register(r'vehicle', vehicleViewSet, base_name='vehicle')
router.register(r'availability', availabilityViewSet, base_name='availability')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'media/$' , mediaView.as_view()),
    url(r'media/(?P<pk>\d+)/$' , mediaView.as_view()),
    url(r'listingView/$', listingView.as_view()),
    ]
