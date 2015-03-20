# -*- coding: utf-8 -*-

import ctypes
from ctypes import *
from ctypes.wintypes import HWND, UINT

encDll = ctypes.WinDLL("F:\\fcrypt_e.dll")
#encDll = ctypes.CDLL("F:\\fcrypt_e.dll")
prototype = WINFUNCTYPE(c_int, HWND, c_char_p, c_char_p, c_char_p, UINT)
paramflags = (1, "hwnd", 0), (1, "PlainFilePathName", "F:\\test.txt"), (1, "EncFilePathName", "F:\\enc_test.txt"), \
             (1, "password", "1234567"), (1, "flags", 0)

EncryptFile = prototype(("DSFC_EncryptFile", encDll), paramflags)

EncryptFile()