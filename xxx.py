#-*- coding: utf-8 -*-

_value = u'이것은 한글입니다.'

_len_value = len(_value)

print _len_value

_list_value = list(_value)

for i in range(_len_value):
    print i, ' 번째 글자는 ...', _list_value[i]