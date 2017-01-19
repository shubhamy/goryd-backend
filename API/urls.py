from django.conf.urls import include, url
from rest_framework_jwt.views import obtain_jwt_token
from .views import *

urlpatterns = [
    url(r'^alt-token-auth/', obtain_jwt_token),
    url(r'^users/', include('users.urls')),
    url(r'^listing/', include('listing.urls')),
    url(r'^finance/', include('finance.urls')),
    url(r'^support/', include('support.urls')),
    url(r'^booking/', include('booking.urls')),
]
