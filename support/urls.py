from django.conf.urls import include, url
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'feedback' , feedbackViewSet , base_name = 'feedback')
router.register(r'ticket' , ticketViewSet , base_name = 'ticket')
router.register(r'faqs' , faqViewSet , base_name = 'faq')
router.register(r'subscribe', subscriberViewSet, base_name='subscriber')
router.register(r'query', UserQueryViewSet, base_name='userquery')
urlpatterns = [
    url(r'^', include(router.urls)),
    ]
