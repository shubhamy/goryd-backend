from requests import request, ConnectionError
from django.core.files.base import ContentFile
from social.pipeline.partial import partial
from users.models import profile
import datetime
from django.shortcuts import redirect
from users.views import sendOTP, getDetails
from django.contrib.auth.models import User
from backend import settings

@partial
def save_profile(backend, user, response, is_new, *args, **kwargs):
    if backend.name == 'facebook':
        p = profile.objects.filter(user=user)
        if not p.exists():
            user.username = response['email']
            user.first_name = response['name'].split(' ')[0]
            user.last_name = response['name'].split(' ')[-1]
            try:
                user.save()
            except:
                user.delete()
                return {'user': User.objects.get(username=response['email'])}
            else:
                mobile = kwargs['request'].get('mobile')
                # if not mobile:
                #     return redirect('acquire_mobile_number')
                url = 'https://graph.facebook.com/me?fields=birthday,picture&access_token={0}'.format(response['access_token'])
                try:
                    resp = request('GET', url, params={'type': 'large'})
                    resp.raise_for_status()
                    dob = datetime.datetime.strptime(resp.json()['birthday'], '%m/%d/%Y').date()
                    dpurl = resp.json()['picture']['data']['url']
                except ConnectionError:
                    raise ConnectionError
                p = profile.objects.create(user=user, dob=dob, mobile=mobile)
                p.dp.save(u'', ContentFile(request('GET', dpurl).content), save=True)
                sendOTP(user)
        else:
            print "facebook Login successful"
    elif backend.name == 'google-oauth2':
        p = profile.objects.filter(user=user)
        if not p.exists():
            user.username = response['emails'][0]['value']
            user.first_name = response['name']['givenName']
            user.last_name = response['name']['familyName']
            try:
                user.save()
            except:
                user.delete()
                return {'user': User.objects.get(username=response['emails'][0]['value'])}
            else:
                mobile = kwargs['request'].get('mobile')
                try:
                    dob = datetime.datetime.strptime(response['birthday'], '%Y-%m-%d').date()
                    if not dob.year:
                        raise ValidationError('Invalid Birth Year')
                except:
                    dob = ''#kwargs['request'].get('dob')
                if not mobile:
                    return redirect('acquire_mobile_number')
                dpurl = response['image']['url']
                p = profile.objects.create(user=user, mobile=mobile)
                p.dp.save(u'', ContentFile(request('GET', dpurl).content), save=True)
                sendOTP(user)
        else:
            print "Google Login successful"
    elif backend.name == 'twitter':
        p = profile.objects.filter(user=user)
        if not p.exists():
            try:
                email = response['email']
            except:
                user.delete()
                print("\033[31m[-] You are unauthorized to access email addresses. Fatal Error.\033[37m \n")
                return
            else:
                user.username = email
                user.first_name = response['name'].split(' ')[0]
                try:
                    user.save()
                except:
                    user.delete()
                    return {'user': User.objects.get(username=email)}
                else:
                    mobile = kwargs['request'].get('mobile')
                    dob = kwargs['request'].get('dob')
                    if not mobile and not dob:
                        return redirect('acquire_mobile_number')
                    dpurl = response['profile_image_url']
                    p = profile.objects.create(user=user, mobile=mobile)
                    p.dp.save(u'', ContentFile(request('GET', dpurl).content), save=True)
                    sendOTP(user)
        else:
            print 'twitter successful login'
    elif backend.name == 'linkedin':
        p = profile.objects.filter(user=user)
        if not p.exists():
            try:
                email = response.get('emailAddress')
            except:
                user.delete()
                print("\033[31m[-] You are unauthorized to access email addresses. Fatal Error.\033[37m \n")
                return
            else:
                user.username = email
                user.first_name = response['firstName']
                user.last_name = response['lastName']
                try:
                    user.save()
                except:
                    user.delete()
                    return {'user': User.objects.get(username=email)}
                else:
                    #getting mobile number and dob and email
                    mobile = kwargs['request'].get('mobile')
                    dob = ''#kwargs['request'].get('dob')
                    if not mobile and not dob:
                        return redirect('acquire_mobile_number')
                    p = profile.objects.create(user=user, mobile=mobile)
                    #no dp in case of linkedin
                    #p.dp.save(u'', ContentFile(request('GET', dpurl).content), save=False)
                    sendOTP(user)
        else:
            print 'linkedin successful login'
