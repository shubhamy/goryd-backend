from finance.views import calculate_total_rent
from .models import *
from collections import OrderedDict
from requests import request, ConnectionError
from django.conf import settings
import polyline

def filterSearchResults(fromDateTime, toDateTime, latitude, longitude, sortBy='totalRent'):
    # getting all the available vehicles fromDateTime to toDateTime
    LENGTH = int(str(toDateTime.date() - fromDateTime.date()).split(' ')[0])
    vehicles = {}
    flag = 0
    for a in availability.objects.filter(date__range=[fromDateTime.date(), toDateTime.date()]):
        for v in a.vehicle.filter(active=True, isListingComplete=True, verified=True):
            try:
                vehicles[v] += 1
            except:
                if not flag:
                    vehicles[v] = 0
        flag = 1
    print vehicles

    filteredVehicles = {}
    for k,v in vehicles.items():
        if v == LENGTH:
            filteredVehicles[k] = v
    if filteredVehicles == {}:
        return None
    #calculate distance
    origins = [(float(latitude), float(longitude)),]
    destinations = []
    for k,v in filteredVehicles.items():
        try:
            if k.address.lat and k.address.lon:
                destinations.append((float(k.address.lat), float(k.address.lon)))
            else:
                filteredVehicles.pop(k)
        except ConnectionError:
            pass
    distances = geoDistance(origins, destinations)
    # sorting
    count = 0
    if sortBy == 'totalRent':
        for k,v in filteredVehicles.items():
            filteredVehicles[k] = (calculate_total_rent(k.weekdayPrice, k.weekendPrice, fromDateTime, toDateTime), distances[count])
            count+=1
        return OrderedDict(sorted(filteredVehicles.items(), key=lambda t: t[1][0], reverse=False))
    elif sortBy == 'distance':
        filteredVehicles = dict(zip(filteredVehicles.keys(), (distances, distances)))
        return OrderedDict(sorted(filteredVehicles.items(), key=lambda t: t[1][0], reverse=False))
    elif sortBy == 'deposit':
        for k,v in filteredVehicles.items():
            filteredVehicles[k] = (k.deposit, distances[count])
            count+=1
        return OrderedDict(sorted(filteredVehicles.items(), key=lambda t: t[1][0], reverse=False))

def geoDistance(org, dest):
    retVal = []
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=enc:{0}:&destinations=enc:{1}:&key={2}".format(polyline.encode(org, 5), polyline.encode(dest, 5), settings.GOOGLE_API_MAP_KEY)
        response = request('GET', url)
        for d in response.json()['rows'][0]['elements']:
            retVal.append(d['distance']['text'])
    except:
        for d in destinations:
            retVal.append('Unknown')
    return retVal
