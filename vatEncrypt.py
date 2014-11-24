#-*- coding: utf-8 -*-
__author__ = 'KC'

from ctypes import *

encDll = cdll.LoadLibrary("d:\\fcrypt_es.dll")

ret = encDll.DSFC_EncryptFile(0, "D:\\test.txt", "D:\\enc_test.txt", "1234567", 1)

print '결과값은 > ', ret




