
# Python program to find SHA256 hexadecimal hash string of a file
import hashlib
from embercode.data import * 
from embercode.data import __1_2_upload
from embercode.data import __1_2_download

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

def download_operate():
    for file in read_keys():
        with open(file, "rb") as f:
            bytes = f.read() # read entire file as bytes
            readable_hash = hashlib.sha256(bytes).hexdigest();
            print('readable_hash', readable_hash)
            __1_2_download(readable_hash)


# upload = __1_2_upload(path)