# -*- coding: utf-8 -*-

"""
부가세 파일 신고를 위한, 파일 생성 Application,
Node.js 에서 해당 요청이 들어온 후에, Python 을 통해
실행이 된다.
"""

import sys

sys.path.append(r'C:\Python27\Lib')
sys.path.append(r'C:\Python27\Lib\site-packages')

import pymongo
import json
import urllib2
import os
import re
from numbers import Number

_company = {}
_mongo = {}

'''
텍스트만 가져오는 구문,
/[^a-z|^A-Z|^0-9]/gi,''
'''


def get_only_text(orig_str):
    print '***', orig_str
    string_ = re.sub('-', '', orig_str)
    print string_
    return ''.join(string_)

'''
회사정보를 가져오는 구문,
'''


def get_company(company_code):
    _company_config = get_config_obj('Server')
    _config = _company_config['BSE']
    _server_name = _config['server']
    _server_port = _config['ports']

    url = u''.join(['http://', _server_name, ':', _server_port, '/api/co/', company_code])
    print url
    try:
        resp = urllib2.urlopen(url).read()
        company_info = json.loads(resp.decode('utf8'))

        return company_info[0]

    except:
        pass

    return 0


'''
Company json 파일을 읽어서 객체를 넘겨주는 함수,
여기서 Exception 또는 Validation 처리도 진행해야 됨.
'''


def get_config_obj(json_name):
    file_path = u''.join([os.getcwd(), '\\config\\', json_name, '.json'])
    try:
        with open(file_path) as jsonObj:
            json_data = json.load(jsonObj)

        return json_data
    except EnvironmentError as e:
        print u'EnvironmentError >>>>> ', str(e)
    except:
        print u'Uncaught Error', sys.exc_info()[0]

    return 0


'''
Mongo 에 접속해서, 접속한 결과 Collections 을
리턴하는 Function.
'''


def db_connection(document_name, company_name):
    try:
        if document_name == '':
            raise TypeError(u'Document name has not defined')

        client = pymongo.MongoClient()
        db = client[company_name]
        collection = db[document_name]

        return collection
    except pymongo.errors.ConnectionFailure as e:
        print 'Connection Error occurred :', str(e)
    except TypeError as e:
        print 'Exception :: ', str(e)

'''
테이블의 값을 가져오는 구문, 필요한 값을 가져온다.
'''


def get_table_data(company_name, document_name, ret_key):
    print 'Company Name..', company_name, 'Document Name...', document_name, 'Key....[', ret_key, ']'
    collection = db_connection(document_name.lower(), company_name)
    documents = collection.find_one({"VATKEY": ret_key})

    return documents


'''
대상의 모든 데이터를 한꺼번에 가져와서 한 Dictionary 에 담아서 리턴
@param company_name  회사이름으로, Mongo Database Name
@param ret_key 년도/기수/정기신고 에 대한 키값
@param target_list 대상 Document 목록 (이는 Mongo의 Collection 에 해당함)
'''


def get_target_data(company_name, ret_key, target_list):
    print 'Company_name > ', company_name, 'Retrieve Key...>', ret_key, 'Target List..', target_list

    if target_list is None or '':
        raise ValueError('Target Value is not defined.')

    #ret_key 에는 년도/기수까지만 받아서, target_list 의 값과 합해서 키를 만들 것.
    _result = {}

    for target_value in target_list:
        print 'One target ....', target_value
        if target_list == '':
            continue
        key_ = ''.join([ret_key, target_value, company_name])
        print 'The key is....', key_
        result_ = get_table_data(company_name, target_value, key_)
        _result[target_value] = result_

    return _result


'''
파일경로를 받아서, 해당 경로에 있는 Json 을 Object 로 변환하여
리턴하는 Function.
'''


def get_json_obj(file_path):
    try:
        if file_path == '':
            raise TypeError(u'File path has not defined')
        with open(file_path) as jsonObj:
            json_data = json.load(jsonObj)

        return json_data
    except OSError as e:
        print 'System Exception :', str(e)
    except TypeError as e:
        print 'Exception :: ', str(e)


'''
파일에 한 라인을 넣기....
'''


def write_line(_define, _file_name):

    if _define is None or '':
        raise ValueError('JSON Value is not defined..')

    #키 값을 Tuple 에 담아서 Sorting 한다.
    _define_keys = tuple(_define.keys())
    _sorted_keys = sorted(_define_keys)
    _report = []

    #Sorting 한 순서대로 라인을 만든다.
    with open(_file_name, 'a') as f:
        for define_items in _sorted_keys:
            _line_define = _define[define_items]
            _result = make_line(_line_define)
            print '[', _result, ']'
            _report.append(_result)

        _report.append('\n')
        f.write(''.join(_report))


'''
값 채우기
@param _field_value 정의된 값
@param _len 필드의 길이
@param _blank 빈 값에 넣기
@param _line 미리 선언한 라인
'''


def fill_line(_field_value, _len, _blank, _line):
    if _field_value is None:
        return
    #필드의 길이를 잰다.

    if isinstance(_field_value, Number):
        _field_value = str(_field_value)

    _len_value = len(_field_value)

    #값이 정의된 길이보다 길면, 에러...
    if _len_value > int(_len):
        raise ValueError('bigger than pre defined value....')

    if not _len_value == 0:

        if _blank == '0':
            _list_value = list(_field_value)
            _index = int(_len) - _len_value - 1
            for i in range(_len_value):
                _line[_index + i] = _list_value[i]
        else:
            _list_value = list(_field_value)
            for idx, items in enumerate(_list_value):
                _line[idx] = items

'''
필요한 값과, 구조를 받아서 Line 을 생성하는 Function
'''


def make_line(_define):
    global _company
    global _mongo

    # 넘어온 Parameter 를 체크한다.
    if _define is None or '':
        raise ValueError(u'넘겨온 값이 없습니다. make_line')

    # 리턴할 값 초기화
    _line = []
    _len = _define['length']

    try:
        # 길이 값 점검.
        if _len is None or int(_len) == 0:
            raise ValueError(u'길이 값이 정의되지 않았습니다')

        # 길이 만큼 공간을 넣어준다.
        _blank = _define['blank']
        if _blank == '':
            _blank = u' '

        for i in range(int(_len)):
            _line.append(_blank)

        #값의 길이를 측정해서,

        _field_value = _define['value']

        fill_line(_field_value, _len, _blank, _line)

        if 'table' in _define:
            if _define['table'] == '':
                _db_field_value = None
            elif _define['table'] == 'BSE':
                _db_field_value = None
            elif _define['table'] == 'company':
                _db_field_value = get_only_text(_company[_define['field']])
            else:
                _table = _mongo[_define['table']]
                _db_field_value = _table[_define['field']]

            print 'Field Value..........>', _db_field_value
            fill_line(_db_field_value, _len, _blank, _line)

    except ValueError as e:
        print 'Value Error :', str(e)
    except TypeError as e:
        print 'Type Error : ', str(e)

    return u''.join(_line).encode('utf-8')


def make_vat_file(target_list, vat_key, company_code):
    global _company
    global _mongo

    try:
        print 'Document Name ::', target_list, 'VATKEY ::', vat_key
        file_path = ''.join([os.getcwd(), '\\config\\_Report.json'])

        # Company 정보 가져오기
        _company = get_company(company_code)
        print 'Company Information .. ', _company
        # Mongo에 있는 대상의 값을 모두 가져오기.
        _mongo = get_target_data(company_code, vat_key, target_list)
        print 'Mongo Database Information... ', _mongo
        # 해당 월에 필요한 정보 모두 가져오기

        # Header 만들기...
        #json 에서 값을 가져와서 Dict 로 담는다.
        _json = get_json_obj(file_path)

        #가져온 DICT 자료에서 Header 만 가져온다.
        _header_define = _json['HEADER']

        write_line(_header_define, 'test.txt')

        #넘어온 KEY list 를 돌리면서,

        for target_doc in target_list:
            if target_doc == '':
                continue
            _doc_define = _json[target_doc]
            write_line(_doc_define, 'test.txt')

        #각각 파일 말기....
    except IndexError as e:
        print 'Index Error: ', str(e)
    except IOError as e:
        print 'IO Error : ', str(e)
    except ValueError as e:
        print 'Value Error', str(e)

    return True


# 메인 함수.
if __name__ == "__main__":
    # 파일신고 대상 목록 KEY 를 담은 LIST or DIC 같은 것들..에 담아서
    # 넘길것.
    result = make_vat_file(['V104', 'V101'], '201411', 'KIMEX')
    sys.exit(result)

