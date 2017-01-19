# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
import pandas as pd
#import numpy as np
import requests

#load data

#pin = pd.read_csv('all_india_PO_list_without_APS_offices_ver2_lat_long.csv')
#pin=pin.rename(columns = {'officename':'officeName','Deliverystatus':'deliveryStatus','divisionname':'divisionName','regionname':'regionName','circlename':'circleName','Taluk':'taluk','Districtname':'districtName','statename':'stateName','Telephone':'telephone','Related Suboffice':'relatedSuboffice','Related Headoffice':'relatedHeadoffice'})
#pin = pin[['officeName','pincode','stateName','districtName','taluk']]
#pin['lat'] = 0.0
#pin['lng'] = 0.0
#pin_del= pin[pin['stateName']=='DELHI'].reset_index(drop=True)
pin_del = pd.read_csv('pin_f.csv')
with open('log.txt', 'r+') as q:
    start = int(q.readline())
    q.close()
#log = open('log2.txt','w')
for i in range(start,len(pin_del)):
    input_pin = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?types=geocode&language=in&key=AIzaSyDqZoDeSwSbtfkFawD-VoO7nx2WLD3mCgU&input='
    input_place = 'https://maps.googleapis.com/maps/api/place/details/json?key=AIzaSyDqZoDeSwSbtfkFawD-VoO7nx2WLD3mCgU&placeid='
    offcname_i  = str(pin_del['officeName'][i]).split()[0]
    statename_i = str(pin_del['stateName'][i]).split()[0]
    input_pin += offcname_i + ',' + statename_i
    r = requests.get(input_pin)
    p = r.json()
    i_str = str(i)
    if i%2==1:
    if p['status'] == 'OK':
        place_id = str(p['predictions'][0]['place_id'])
        input_place += place_id
        q = requests.get(input_place)
        qr = q.json()
        if qr['status']== 'OVER_QUERY_LIMIT':
            break
        pin_del['lat'][i]= qr['result']['geometry']['location']['lat']
        pin_del['lng'][i]= qr['result']['geometry']['location']['lng']
    if p['status']== 'OVER_QUERY_LIMIT':
        break

pin_f = pin_del.to_csv('pin_f.csv')
i_str = str(i)
q= open('log.txt', 'r+')
q.write(i_str)
if i == len(pin_del):
    a= pin_del.to_dict(orient='index')
    b = []
    for i in range(len(pin_del)):
        b.append({'model' : 'listing.pin' , 'pk' : i+1 , 'fields' : a[i]})
    with open('pincode.json', 'w') as f:
        f.write(json.dumps(b))
    pinJson = json.dumps(b)
else:
    print 'Not Complete Check: ' + p['status']
