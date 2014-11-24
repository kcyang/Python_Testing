# -*- coding: utf-8 -*-
# 오류처리 및 코드를 최대한 최적화 할 것.
import sys
import re


def get_next(orig_number):

    number_result = map(int, re.findall(r'\d+', orig_number))

    string = re.match(r'[a-zA-Z]+', orig_number).group()

    number = number_result[0] + 1

    result_array = []

    result_array.append(string)
    result_array.append(str(number))

    next_number = ''.join(result_array)

    return next_number



# 메인 함수.

if __name__ == "__main__":
    result = get_next('AA91231')
    print result
    sys.exit()