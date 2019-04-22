#!/usr/bin/env python3

import urllib.parse
import urllib.request
import os

url = "http://127.0.0.1:5000/direction?"

data = {}
args = ['src', 'origin', 'destination', 'rank_preference']
for x in args:
    if x in os.environ:
        data[x] = os.environ[x]
    else:
        data[x] = input(x + ": ")

url += urllib.parse.urlencode(data)

response = urllib.request.urlopen(url)
print(response.read().decode())
