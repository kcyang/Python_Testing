# -*- coding: utf-8 -*-
import sys

sys.path.append(r'C:\Python27\Lib')
sys.path.append(r'C:\Python27\Lib\site-packages')

import pymongo
import json
import urllib2
import os
import re
import time
from numbers import Number
import datetime

_company = {}
_mongo = {}
_bse = {}
_V101_1 = {}
_V101_2 = {}
_V101_3 = {}
_V104_1 = {}
_V105_1 = {}
_V109_3 = {}
_V110_3 = {}
_V106 = {}
_V164_1 = {}
_V174_1 = {}


def get_only_text(orig_str):

    if isinstance(orig_str, Number):
        return orig_str

    if isinstance(orig_str, unicode):
        string_ = re.sub('-', '', orig_str)
        string_ = string_.strip()
        return ''.join(string_)

    return orig_str


def get_company(company_code):
    _company_config = get_config_obj('Server')
    _config = _company_config['BSE']
    _server_name = _config['server']
    _server_port = _config['ports']

    url = ''.join(['http://', _server_name, ':', _server_port, '/api/co/', company_code])
    print url
    try:
        resp = urllib2.urlopen(url).read()
        company_info = json.loads(resp.decode('utf8'))

        return company_info[0]
    except:
        pass

    return 0


def get_config_obj(json_name):
    file_path = ''.join([os.getcwd(), '\\config\\', json_name, '.json'])
    try:
        with open(file_path) as jsonObj:
            json_data = json.load(jsonObj)

        return json_data
    except EnvironmentError as e:
        print 'EnvironmentError >>>>> ', str(e)
    except:
        print 'Uncaught Error', sys.exc_info()[0]

    return 0


def db_connection(document_name, company_name):
    try:
        if document_name == '':
            raise TypeError('Document name has not defined')

        client = pymongo.MongoClient()
        db = client[company_name]
        collection = db[document_name]

        return collection
    except pymongo.errors.ConnectionFailure as e:
        print 'Connection Error occurred :', str(e)
    except TypeError as e:
        print 'Exception :: ', str(e)


def get_table_data(company_name, document_name, ret_key):
    print 'Company Name..', company_name, 'Document Name...', document_name, 'Key....[', ret_key, ']'
    collection = db_connection(document_name.lower(), company_name)
    documents = collection.find_one({"VATKEY": ret_key})

    return documents



def get_target_data(company_name, ret_key, target_list):
    print 'Company_name > ', company_name, 'Retrieve Key...>', ret_key, 'Target List..', target_list

    if target_list is None or '':
        raise ValueError('Target Value is not defined.')

    _result = {}

    for target_value in target_list:
        print 'One target ....', target_value
        if target_list == '':
            continue
        if target_value == 'V109':
            target_value = 'V104-1'
        if target_value == 'V110':
            target_value = 'V105-1'

        key_ = ''.join([ret_key, target_value, company_name])
        print 'The key is....', key_
        result_ = get_table_data(company_name, target_value, key_)
        _result[target_value] = result_

    return _result


def get_json_obj(file_path):
    try:
        if file_path == '':
            raise TypeError('File path has not defined')
        with open(file_path) as jsonObj:
            json_data = json.load(jsonObj)

        return json_data
    except OSError as e:
        print 'System Exception :', str(e)
    except TypeError as e:
        print 'Exception :: ', str(e)



def write_line(_define, _file_name):

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')


    _define_keys = tuple(_define.keys())
    _sorted_keys = sorted(_define_keys)
    _report = []

    with open(_file_name, 'a') as f:
        for define_items in _sorted_keys:
            _line_define = _define[define_items]
            _result = make_line(_line_define)
            print '[', _result, ']'
            _report.append(str(_result))

        _report.append('\n')
        f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def fill_line(_field_value, _len, _blank, _line):
    if _field_value is None:
        return
    if _field_value == '':
        return

    if isinstance(_field_value, Number):
        _field_value = str(_field_value)

    if isinstance(_field_value, datetime.datetime):
        if _field_value.year <= 1900:
            _field_value = ''
        else:
            _field_value = _field_value.strftime('%Y%m%d')

    _len_value = len(_field_value)

    if _len_value > int(_len):
        raise ValueError('bigger than pre defined value....')

    if not _len_value == 0:
        if _blank == '0':
            _field_value_l = float(_field_value)
            if _field_value_l < 0:
                _field_value = str(long(abs(_field_value_l)))
                _line[0] = '-'
            else:
                _field_value = float(_field_value)
                _field_value = str(long(_field_value))

            _len_value = len(_field_value)

            _list_value = list(_field_value)
            _index = int(_len) - _len_value

            for i in range(_len_value):
                _line[_index + i] = _list_value[i]

        else:

            #print 'T[', get_only_text(_field_value), '] LEN[', len(get_only_text(_field_value)), ']'

            '''
            _list_value = list(_temp)
            #_list_value = list(get_only_text(_field_value))
            print 'line length.....', len(_line), 'value_length...', len(_list_value)
            for idx, items in enumerate(_list_value):
                if idx >= len(_list_value):
                    continue
                _line[idx] = items
            '''

            #_temp_text = unicode(get_only_text(_field_value)).encode('cp949')
            _temp_text = get_only_text(_field_value)
            print 'XXX > ', str(_temp_text) , 'LEN ..> ', len(_temp_text)

            _temp_text = unicode(_temp_text).encode('cp949')

            print 'XXX > ', str(_temp_text) , 'LEN ..> ', len(_temp_text)
            #_temp_text = unicode(_temp_text,'cp949').encode('utf-8')
            print 'XXX > ', str(_temp_text) , 'LEN ..> ', len(_temp_text)

            _list_value = list(_temp_text)
            for idx, items in enumerate(_list_value):
                _line[idx] = items


def make_line(_define):
    global _company
    global _mongo
    global _V101_1
    global _V101_2
    global _V101_3
    global _V104_1
    global _V105_1
    global _V109_3
    global _V110_3
    global _V106
    global _V164_1
    global _V174_1

    if _define is None or '':
        raise ValueError('make_line')

    _line = []
    _len = _define['length']

    try:
        if _len is None or int(_len) == 0:
            raise ValueError('xxxxxxxxxxxxxxxxxxxxxxx')
        _blank = _define['blank']
        if _blank == '':
            _blank = ' '

        for i in range(int(_len)):
            _line.append(_blank.encode('utf-8'))

        _field_value = _define['value']

        fill_line(_field_value, _len, _blank, _line)

        if 'table' in _define:
            if _define['table'] == '':
                _db_field_value = None
            elif _define['table'] == '_V101_1':
                _db_field_value = get_only_text(_V101_1[_define['field']])
            elif _define['table'] == '_V101_2':
                _db_field_value = get_only_text(_V101_2[_define['field']])
            elif _define['table'] == '_V101_3':
                _db_field_value = get_only_text(_V101_3[_define['field']])
            elif _define['table'] == '_V104_1':
                _db_field_value = get_only_text(_V104_1[_define['field']])
            elif _define['table'] == '_V104_2':
                _table = _mongo['V104']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V104_3':
                _table = _mongo['V104']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V105_1':
                _db_field_value = get_only_text(_V105_1[_define['field']])
            elif _define['table'] == '_V105_2':
                _table = _mongo['V105']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V105_3':
                _table = _mongo['V105']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V109_1':
                _table = _mongo['V104-1']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V109_2':
                _table = _mongo['V104-1']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V109_4':
                _table = _mongo['V104-1']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V109_3':
                _db_field_value = get_only_text(_V109_3[_define['field']])
            elif _define['table'] == '_V110_2':
                _table = _mongo['V105-1']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V110_4':
                _table = _mongo['V105-1']
                _db_field_value = _table.get(_define['field'])
            elif _define['table'] == '_V110_3':
                _db_field_value = get_only_text(_V110_3[_define['field']])
            elif _define['table'] == 'V106':
                _db_field_value = get_only_text(_V106[_define['field']])
            elif _define['table'] == '_V164_1':
                _db_field_value = get_only_text(_V164_1[_define['field']])
            elif _define['table'] == '_V174_1':
                _db_field_value = get_only_text(_V174_1[_define['field']])
            elif _define['table'] == 'BSE':
                _db_field_value = get_only_text(_bse[_define['field']])
            elif _define['table'] == 'V104':
                _db_field_value = get_only_text(_bse[_define['field']])
            elif _define['table'] == 'company':
                _db_field_value = get_only_text(_company[_define['field']])
            else:
                _table = _mongo[_define['table']]
                if _define['field'] in _table:
                    _db_field_value = _table[_define['field']]
                else:
                    _db_field_value = None

            print 'Field Value..........>', _db_field_value

            if 'multi' in _define:
                if _define['multi'] == 'Y':
                    _temp = int(_db_field_value)
                    if _temp < 0:
                        _temp_str = str(_temp)
                        _temp_last = _temp_str[len(_temp_str)]

                        if _temp_last == '0':
                            _multi = '}'
                        elif _temp_last == '1':
                            _multi = 'J'
                        elif _temp_last == '2':
                            _multi = 'K'
                        elif _temp_last == '3':
                            _multi = 'L'
                        elif _temp_last == '4':
                            _multi = 'M'
                        elif _temp_last == '5':
                            _multi = 'N'
                        elif _temp_last == '6':
                            _multi = 'O'
                        elif _temp_last == '7':
                            _multi = 'P'
                        elif _temp_last == '8':
                            _multi = 'Q'
                        elif _temp_last == '9':
                            _multi = 'R'

                        _multi_str = _temp_str[:len(_temp_str)] + _multi
                    else:
                        _multi_str = str(_temp)

                    if 'dpoint' in _define:
                        if int(_define.get('dpoint')) > 0:
                            _result = ['0'] * int(_define['dpoint'])

                            _temp = _db_field_value - int(_db_field_value)
                            if _temp != 0:
                                _temp = str(abs(round(_temp, int(_define['dpoint']))))[2:]
                                _temp_l = list(_temp)
                                for i in range(len(_temp)):
                                    _result[i] = _temp_l[i]

                            _dpoint_str = ''.join(_result)
                            _db_field_value = _multi_str + _dpoint_str

                    else:
                        _db_field_value = _multi_str

            fill_line(_db_field_value, _len, _blank, _line)

    except ValueError as e:
        print 'Value Error :', str(e)
    except TypeError as e:
        print 'Type Error : ', str(e)

    return ''.join(_line)


def make_bse(vat_key):
    global _bse
    _bse['YEAR'] = vat_key[:4]
    _bse['TYPE'] = vat_key[4:]
    _bse['GUA_PYO_YU'] = '01'

    if _bse['TYPE'] == '11':
        _bse['GISU'] = '01'
        _bse['SINGO'] = '03'
        _bse['CHASU'] = 'C17'
        _bse['VATFROM'] = _bse['YEAR']+'0101'
        _bse['VATTO'] = _bse['YEAR']+'0331'
        _bse['SFROM'] = vat_key[2:4]+'0101'
        _bse['STO'] = vat_key[2:4]+'0331'
        _bse['V109_GISU'] = '1'
        _bse['V109_SINGO'] = '1'
        _bse['V141YEARMAN'] = _bse['YEAR']+'03'
        _bse['V164_GISU'] = '1'
        _bse['V164_SINGO'] = '3'
    elif _bse['TYPE'] == '12':
        _bse['GISU'] = '01'
        _bse['SINGO'] = '01'
        _bse['CHASU'] = 'C07'
        _bse['VATFROM'] = _bse['YEAR']+'0401'
        _bse['VATTO'] = _bse['YEAR']+'0630'
        _bse['SFROM'] = vat_key[2:4]+'0401'
        _bse['STO'] = vat_key[2:4]+'0630'
        _bse['V109_GISU'] = '1'
        _bse['V109_SINGO'] = '2'
        _bse['V141YEARMAN'] = _bse['YEAR']+'06'
        _bse['V164_GISU'] = '1'
        _bse['V164_SINGO'] = '6'
    elif _bse['TYPE'] == '21':
        _bse['GISU'] = '02'
        _bse['SINGO'] = '03'
        _bse['CHASU'] = 'C17'
        _bse['VATFROM'] = _bse['YEAR']+'0701'
        _bse['VATTO'] = _bse['YEAR']+'0930'
        _bse['SFROM'] = vat_key[2:4]+'0701'
        _bse['STO'] = vat_key[2:4]+'0930'
        _bse['V109_GISU'] = '2'
        _bse['V109_SINGO'] = '1'
        _bse['V141YEARMAN'] = _bse['YEAR']+'09'
        _bse['V164_GISU'] = '2'
        _bse['V164_SINGO'] = '3'
    elif _bse['TYPE'] == '22':
        _bse['GISU'] = '02'
        _bse['SINGO'] = '01'
        _bse['CHASU'] = 'C07'
        _bse['VATFROM'] = _bse['YEAR']+'1001'
        _bse['VATTO'] = _bse['YEAR']+'1231'
        _bse['SFROM'] = vat_key[2:4]+'1001'
        _bse['STO'] = vat_key[2:4]+'1231'
        _bse['V109_GISU'] = '2'
        _bse['V109_SINGO'] = '2'
        _bse['V141YEARMAN'] = _bse['YEAR']+'12'
        _bse['V164_GISU'] = '2'
        _bse['V164_SINGO'] = '6'
    else:
        pass
    _bse['REPORTDATE'] = time.strftime('%Y%m%d')
    _bse['REPORTSDATE'] = (time.strftime('%Y%m%d'))[2:]
    _bse['YEARGISU'] = _bse['YEAR']+_bse['GISU']


'''
make_v101_1(1, '01', _json['_V101_1'], 'test.txt')
'''


def make_v101_1(flag_, type_, _define, _file_name, _uptae, _jonmok, _upjong, _amt):
    global _V101_1

    _V101_1 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    if flag_ == 1 or long(_amt) > 0:
        _V101_1 = {
            "DOCTYPE": type_,
            "UPTAE": _uptae,
            "JONGMOK": _jonmok,
            "UPJONG": _upjong,
            "AMT": str(_amt)
        }

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))

'''
make_v101_2('211', _json['_V101_2'], 'test.txt')
'''


def make_v101_2(type_, _define, _file_name, _amt, _tax):
    global _V101_2

    _V101_2 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    if long(_tax) > 0 or long(_amt) > 0:
        _V101_2 = {
            "DOCTYPE": type_,
            "AMT": str(_amt),
            "TAX": str(_tax)
        }

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))

'''
make_v101_3('B1100', _json['_V101_3'], 'test.txt')
'''


def make_v101_3(type_, _define, _file_name, _amt, _tax):
    global _V101_3

    _V101_3 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    if long(_tax) > 0 or long(_amt) > 0:
        _V101_3 = {
            "DOCTYPE": type_,
            "AMT": str(_amt),
            "TAX": str(_tax)
        }

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_v104_1(_define, _file_name, _v104):
    global _V104_1

    _V104_1 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v104_item in _v104:
        _V104_1 = _v104_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_one_record(_define, _file_name):

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    _define_keys = tuple(_define.keys())
    _sorted_keys = sorted(_define_keys)
    _report = []

    with open(_file_name, 'a') as f:
        for define_items in _sorted_keys:
            _line_define = _define[define_items]
            _result = make_line(_line_define)
            print '[', _result, ']'
            _report.append(str(_result))

        _report.append('\n')
        f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_v105_1(_define, _file_name, _v105):
    global _V105_1

    _V105_1 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v105_item in _v105:
        _V105_1 = _v105_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_v109_3(_define, _file_name, _v109):
    global _V109_3

    _V109_3 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v109_item in _v109:
        _V109_3 = _v109_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))



def make_v110_3(_define, _file_name, _v110):
    global _V110_3

    _V110_3 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v110_item in _v110:
        _V110_3 = _v110_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_v106(_define, _file_name, _v106):
    global _V106

    _V106 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v106_item in _v106:
        _V106 = _v106_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))

def make_v164(_define, _file_name, _v164):
    global _V164_1

    _V164_1 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v164_item in _v164:
        _V164_1 = _v164_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_v174(_define, _file_name, _v174):
    global _V174_1

    _V174_1 = {}

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    for _v174_item in _v174:
        _V174_1 = _v174_item

        _define_keys = tuple(_define.keys())
        _sorted_keys = sorted(_define_keys)
        _report = []

        with open(_file_name, 'a') as f:
            for define_items in _sorted_keys:
                _line_define = _define[define_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(str(_result))

            _report.append('\n')
            f.write(unicode(''.join(_report), 'cp949').encode('utf-8'))


def make_vat_file(target_list, vat_key, company_code):
    global _company
    global _mongo

    try:
        make_bse(vat_key)

        print 'Document Name ::', target_list, 'VATKEY ::', vat_key
        file_path = ''.join([os.getcwd(), '\\config\\_Report.json'])

        _company = get_company(company_code)
        #print 'Company Information .. ', _company
        _mongo = get_target_data(company_code, vat_key, target_list)
        #print 'Mongo Database Information... ', _mongo

        _json = get_json_obj(file_path)

        _header_define = _json['HEADER']

        write_line(_header_define, 'test.txt')

        for target_doc in target_list:
            if target_doc == '':
                continue
            if target_doc == 'V105':
                continue
            if target_doc == 'V110':
                continue

            _doc_define = _json[target_doc]

            if target_doc != 'V106':
                write_line(_doc_define, 'test.txt')

            if target_doc == 'V101':
                #def make_v101_1(flag_, type_, _define, _file_name, _uptae, _jonmok, _upjong, _amt):
                _v101 = _mongo['V101']
                make_v101_1(1, '01', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_1'), _v101.get('TAX_STD_BUS_ITEM_1'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('TAX_STD_BUS_AMT_1'))
                make_v101_1(0, '01', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_2'), _v101.get('TAX_STD_BUS_ITEM_2'), _v101.get('TAX_STD_BUS_CODE_2'), _v101.get('TAX_STD_BUS_AMT_2'))
                make_v101_1(0, '01', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_3'), _v101.get('TAX_STD_BUS_ITEM_3'), _v101.get('TAX_STD_BUS_CODE_3'), _v101.get('TAX_STD_BUS_AMT_3'))

                make_v101_1(0, '02', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_4'), _v101.get('TAX_STD_BUS_ITEM_4'), _v101.get('TAX_STD_BUS_CODE_4'), _v101.get('TAX_STD_BUS_AMT_4'))
                make_v101_1(0, '04', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_1'), _v101.get('TAX_STD_BUS_ITEM_1'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('REDU_CREDIT_TAX'))
                make_v101_1(0, '07', _json['_V101_1'], 'test.txt', _v101.get('TAX_STD_BUS_NAME_1'), _v101.get('TAX_STD_BUS_ITEM_1'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('REDU_ETC_TAX'))
                make_v101_1(0, '08', _json['_V101_1'], 'test.txt', _v101.get('TAXFREE_BUS_TYPE_1'), _v101.get('TAXFREE_BUS_ITEM_1'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('TAXFREE_BUS_AMT_1'))
                make_v101_1(0, '08', _json['_V101_1'], 'test.txt', _v101.get('TAXFREE_BUS_TYPE_2'), _v101.get('TAXFREE_BUS_ITEM_2'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('TAXFREE_BUS_AMT_2'))
                make_v101_1(0, '14', _json['_V101_1'], 'test.txt', _v101.get('TAXFREE_BUS_TYPE_3'), _v101.get('TAXFREE_BUS_ITEM_3'), _v101.get('TAX_STD_BUS_CODE_1'), _v101.get('TAXFREE_BUS_AMT_3'))

                make_v101_2('211', _json['_V101_2'], 'test.txt', _v101.get('ETCGONJE_CRD_GEN_AMT'), _v101.get('ETCGONJE_CRD_GEN_TAX'))
                make_v101_2('212', _json['_V101_2'], 'test.txt', _v101.get('ETCGONJE_CRD_FIXED_AMT'), _v101.get('ETCGONJE_CRD_FIXED_TAX'))
                make_v101_2('230', _json['_V101_2'], 'test.txt', _v101.get('ETCGONJE_EJ_PURCH_AMT'), _v101.get('ETCGONJE_EJ_PURCH_TAX'))
                make_v101_2('270', _json['_V101_2'], 'test.txt', _v101.get('ETCGONJE_RECY_PURCH_AMT'), _v101.get('ETCGONJE_RECY_PURCH_TAX'))
                make_v101_2('291', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCGONJE_GJBUS_PURCH_TAX'))
                make_v101_2('292', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCGONJE_INV_PURCH_TAX'))
                make_v101_2('293', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCGONJE_BDS_PURCH_TAX'))
                make_v101_2('294', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCGONJE_FOREIGN_PURCH_TAX'))
                make_v101_2('310', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCKG_ELECSINGO_TAX'))
                make_v101_2('321', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCKG_ELECBALGUP_TAX'))
                make_v101_2('331', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCKG_TAXI_TAX'))
                make_v101_2('351', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCKG_CASH_TAX'))
                make_v101_2('361', _json['_V101_2'], 'test.txt', 0, _v101.get('ETCKG_ETC_TAX'))
                make_v101_2('410', _json['_V101_2'], 'test.txt', 0, _v101.get('REDU_CREDIT_TAX'))

                make_v101_3('B1100', _json['_V101_3'], 'test.txt', _v101.get('GS_NOBUS_AMT'), _v101.get('GS_NOBUS_TAX'))
                make_v101_3('B3100', _json['_V101_3'], 'test.txt', _v101.get('GS_TAXINV_DELYBAL_AMT'), _v101.get('GS_TAXINV_DELYBAL_TAX'))
                make_v101_3('B3200', _json['_V101_3'], 'test.txt', _v101.get('GS_TAXINV_DELYSUC_AMT'), _v101.get('GS_TAXINV_DELYSUC_TAX'))
                make_v101_3('B3400', _json['_V101_3'], 'test.txt', _v101.get('GS_TAXINV_NOBALGUP_AMT'), _v101.get('GS_TAXINV_NOBALGUP_TAX'))
                make_v101_3('B4300', _json['_V101_3'], 'test.txt', _v101.get('GS_ETAX_DELYBAL_AMT'), _v101.get('GS_ETAX_DELYBAL_TAX'))
                make_v101_3('B4100', _json['_V101_3'], 'test.txt', _v101.get('GS_ETAX_NOSEND_AMT'), _v101.get('GS_ETAX_NOSEND_TAX'))
                make_v101_3('B5100', _json['_V101_3'], 'test.txt', _v101.get('GS_TAXHAP_BADSEND_AMT'), _v101.get('GS_TAXHAP_BADSEND_TAX'))
                make_v101_3('B5300', _json['_V101_3'], 'test.txt', _v101.get('GS_TAXHAP_DELYSNED_AMT'), _v101.get('GS_TAXHAP_DELYSNED_TAX'))
                make_v101_3('A2110', _json['_V101_3'], 'test.txt', _v101.get('GS_BADSINGO_NOSIN_GEN_AMT'), _v101.get('GS_BADSINGO_NOSIN_GEN_TAX'))
                make_v101_3('A2210', _json['_V101_3'], 'test.txt', _v101.get('GS_BADSINGO_NOSIN_BAD_AMT'), _v101.get('GS_BADSINGO_NOSIN_BAD_TAX'))
                make_v101_3('A3110', _json['_V101_3'], 'test.txt', _v101.get('GS_BADSINGO_GSCG_GEN_AMT'), _v101.get('GS_BADSINGO_GSCG_GEN_TAX'))
                make_v101_3('A3210', _json['_V101_3'], 'test.txt', _v101.get('GS_BADSINGO_GSCG_BAD_AMT'), _v101.get('GS_BADSINGO_GSCG_BAD_TAX'))
                make_v101_3('A7100', _json['_V101_3'], 'test.txt', _v101.get('GS_BADNAPBU_AMT'), _v101.get('GS_BADNAPBU_TAX'))
                make_v101_3('A4200', _json['_V101_3'], 'test.txt', _v101.get('GS_ZEROGSSTDBADSINGO_AMT'), _v101.get('GS_ZEROGSSTDBADSINGO_TAX'))
                make_v101_3('B7100', _json['_V101_3'], 'test.txt', _v101.get('GS_CASHSALEBAD_AMT'), _v101.get('GS_CASHSALEBAD_TAX'))
                make_v101_3('B7200', _json['_V101_3'], 'test.txt', _v101.get('GS_BUDONGRENTBAD_AMT'), _v101.get('GS_BUDONGRENTBAD_TAX'))
                make_v101_3('B7300', _json['_V101_3'], 'test.txt', _v101.get('GS_PURCHSPECIAL_KONTO_AMT'), _v101.get('GS_PURCHSPECIAL_KONTO_TAX'))
                make_v101_3('B7400', _json['_V101_3'], 'test.txt', _v101.get('GS_PURCHSPECIAL_DELYKONTO_AMT'), _v101.get('GS_PURCHSPECIAL_DELYKONTO_TAX'))

            elif target_doc == 'V104':

                #write_line(_json['V104'], 'test.txt')  # V104 Header
                _v104_h = _mongo['V104']

                if int(_v104_h['NON_ELEC_TOT_SALES_CNT']) > 0:
                    _v104 = _v104_h['SUB']
                    make_v104_1(_json.get('_V104_1'), 'test.txt', _v104)

                make_one_record(_json.get('_V104_2'), 'test.txt')
                make_one_record(_json.get('_V104_3'), 'test.txt')
                _v105_h = _mongo['V105']

                if int(_v105_h['NON_ELEC_TOT_PURCH_CNT']) > 0:
                    _v105 = _v105_h['SUB']
                    make_v105_1(_json.get('_V105_1'), 'test.txt', _v105)

                make_one_record(_json.get('_V105_2'), 'test.txt')
                make_one_record(_json.get('_V105_3'), 'test.txt')

            elif target_doc == 'V109':
                write_line(_json['_V109_1'], 'test.txt')

                make_one_record(_json.get('_V109_2'), 'test.txt')

                _v109_h = _mongo['V104-1']

                if 'NON_ELEC_TOT_SALES_CNT' in _v109_h:
                    if int(_v109_h.get('NON_ELEC_TOT_SALES_CNT')) > 0:
                        _v109 = _v109_h['SUB']
                        make_v109_3(_json.get('_V109_3'), 'test.txt', _v109)

                make_one_record(_json.get('_V109_4'), 'test.txt')

                make_one_record(_json.get('_V110_2'), 'test.txt')

                _v110_h = _mongo['V105-1']

                if int(_v110_h['ELEC_PSN_PURCH_CNT']) > 0:
                    _v110 = _v110_h['SUB']
                    make_v110_3(_json.get('_V110_3'), 'test.txt', _v110)

                make_one_record(_json.get('_V110_4'), 'test.txt')
            elif target_doc == 'V106':

                _v106_h = _mongo['V106']
                if 'TOT_INTRO_WON_AMT' in _v106_h:
                    if int(_v106_h.get('TOT_INTRO_WON_AMT')) > 0:
                        _v106 = _v106_h['SUB']
                        make_v106(_json.get('V106'), 'test.txt', _v106)

            elif target_doc == 'V164':
                _v164_h = _mongo['V164']
                if 'GE_TOTAL_COUNT' in _v164_h:
                    if int(_v164_h.get('GE_TOTAL_COUNT')) > 0:
                        _v164 = _v164_h['SUB']
                        make_v164(_json.get('_V164_1'), 'test.txt', _v164)

            elif target_doc == 'V174':
                _v174_h = _mongo['V174']
                if 'TOT_COUNT' in _v174_h:
                    if int(_v174_h.get('TOT_COUNT')) > 0:
                        _v174 = _v174_h['SUB']
                        make_v174(_json.get('_V174_1'), 'test.txt', _v174)
            else:
                print 'xxxx'


    except IndexError as e:
        print 'Index Error: ', str(e)
    except IOError as e:
        print 'IO Error : ', str(e)
    except ValueError as e:
        print 'Value Error', str(e)

    return True


if __name__ == "__main__":
    result = make_vat_file(['V101', 'V104', 'V105', 'V109', 'V110', 'V106', 'V141', 'V153', 'V177', 'V149', 'V174'], '201411', 'KIMEX')
    #result = make_vat_file(['V106'], '201411', 'KIMEX')
    sys.exit(result)

