"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from users.views import *
from django.conf import settings
from django.conf.urls.static import static
from API.views import obtain_goryd_token
from rest_framework.authtoken import views
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^api/', include('API.urls')),
    url(r'^register/$', registerView.as_view()),
    url(r'^register/validateOTP/$', validateOTP),
    url(r'^forgotPassword/$', ForgotPassword.as_view()),
    url(r'^forgotPassword/validateOTP/$', validateOTP),
    url(r'^changePassword/$', NewPassword.as_view()),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace ='rest_framework')),
    url(r'^logout/', logoutView , name ='logout'),
    url(r'^api-token-auth/', obtain_goryd_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

if settings.DEBUG:
    urlpatterns +=static(settings.STATIC_URL , document_root = settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
