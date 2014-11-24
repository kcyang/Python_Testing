#-*- coding: utf-8 -*-

import pymongo

# 몽고DB 연결하기
try:
    client = pymongo.MongoClient()
    print "성공적으로 연결되었습니다"

    db = client.test

    collection = db['jsontest']

    key_dic = collection.find_one().keys()

    print key_dic

    for k_item in key_dic:
        if k_item == '_id':
            continue
        print k_item

except pymongo.errors.ConnectionFailure, e:
    print "몽고DB에 연결하지 못했습니다."



