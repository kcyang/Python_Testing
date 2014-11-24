#-*- coding: utf-8 -*-
import json

data = {"a": "AAAAAAAAAAAAAAA", "b": "BBBBBBBBBBBBBBB", "c": "한글"}

json_string = json.dumps(data)

print('Parameters are >>>'+json_string)

json_obj = json.loads(json_string)

print(json_obj.get('c'))