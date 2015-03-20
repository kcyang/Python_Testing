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
import os


'''
Mongo 에 접속해서, 접속한 결과 Collections 을
리턴하는 Function.
'''


def db_connection(document_name):
    try:
        if document_name == '':
            raise TypeError(u'Document name has not defined')

        client = pymongo.MongoClient()
        db = client.BSEVAT
        collection = db[document_name]

        return collection
    except pymongo.errors.ConnectionFailure as e:
        print 'Connection Error occurred :', str(e)
    except TypeError as e:
        print 'Exception :: ', str(e)


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
필요한 값과, 구조를 받아서 Line 을 생성하는 Function
'''


def make_line(_define):
    # 넘어온 Parameter 를 체크한다.
    if _define is None or '':
        raise ValueError(u'넘겨온 값이 없습니다. make_line')

    # 리턴할 값 초기화
    _line = []
    _len = _define['length']
    #print u'필드의 길이 정의는 ...>', _len

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
        _len_value = len(_field_value)

        #print u'값의 길이는 ', _len_value

        #값이 정의된 길이보다 길면, 에러...
        if _len_value > int(_len):
            raise ValueError(u'정의된 길이보다 값이 큽니다....')

        if not _len_value == 0:
            if _blank == '0':
                print u'숫자 값은 > ', _define['value']
                _list_value = list(_field_value)
                _index = int(_len) - _len_value - 1
                for i in range(_len_value):
                    _line[_index + i] = _list_value[i]

            else:
                #print u'스트링 값은 > ', _define['value']
                _list_value = list(_field_value)
                for idx, items in enumerate(_list_value):
                    _line[idx] = items

    except ValueError as e:
        print 'Value Error :', str(e)
    except TypeError as e:
        print 'Type Error : ', str(e)

    return u''.join(_line).encode('utf-8')


def make_vat_file(document_name, vat_key):
    try:
        print 'Document Name ::', document_name, 'VATKEY ::', vat_key
        file_path = ''.join([os.getcwd(), '\\config\\_Report.json'])
        # Header 만들기...
        #json 에서 값을 가져와서 Dict 로 담는다.
        _json = get_json_obj(file_path)

        #가져온 DICT 자료에서 Header 만 가져온다.
        _header_define = _json['HEADER']

        #키 값을 Tuple 에 담아서 Sorting 한다.
        _header_keys = tuple(_header_define.keys())
        _sorted_keys = sorted(_header_keys)
        _report = []
        #Sorting 한 순서대로 라인을 만든다.
        with open('test.txt', 'w+') as f:
            for header_items in _sorted_keys:
                _line_define = _header_define[header_items]
                _result = make_line(_line_define)
                print '[', _result, ']'
                _report.append(_result)

            _report.append('\n')
            f.write(''.join(_report))

        #넘어온 KEY list 를 돌리면서,
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
    result = make_vat_file('V106', '20141201V106')
    sys.exit(result)
