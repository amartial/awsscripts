
from embercode.data import * 
from embercode.data import __1_2_upload

def read_keys():
    keys = []
    with open('emberfiles/ref.txt') as f:
        res = f.readlines()
        # print('lines', lines)
        keys = res[0].split(',')[:-1]

        print(keys)
    return keys

def read_operate():
    for file in read_keys():
        print('__1_2_upload treatment')
        __1_2_upload('emberfiles/' + file)




# upload = __1_2_upload(path)