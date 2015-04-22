# -*- coding: utf-8 -*-

import urllib2
import json

url = 'http://localhost:3000/api/co/KIMEX'

response = urllib2.urlopen(url).read()

data = json.loads(response.decode('utf8'))

print '%1', data