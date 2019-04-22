#!/usr/bin/env python3

import urllib.parse
import urllib.request

url = "http://127.0.0.1:5000/pollution"

data = {}
data['src'] = input('Identification key: ')
data['lat'] = float(input('Latitude of your location: '))
data['lng'] = float(input('Longitude of your location: '))
data['time'] = int(input('Time of the readings: '))
data['pollution'] = float(input('Pollution level: '))

urllib.request.urlopen(url, data=urllib.parse.urlencode(data).encode())
