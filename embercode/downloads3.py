import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

BUCKET_NAME = 'job-bucket001'
OBJECT_NAME = '13ff701a41f55b38134bfe16dd51322e35214bc752cc40b6f50436eaa03e0f5e'
LOCAL_FILE_NAME = "../emberfiles/ember.txt"

def downoadfromS3():
    s3 = boto3.client('s3')
    with open('../emberfiles/ember.txt', 'wb') as f:
        s3.download_fileobj('BUCKET_NAME', 'OBJECT_NAME', f)
        f.seek(0)


def download_s3_file(bucketname, objectname, localfile):
    s3 = boto3.client('s3')
    s3.download_file(BUCKET_NAME, objectname, localfile)

# file1 = open('../s3files/s3key2.txt', 'r')
# count = 0
keys = []
with open('../s3files/s3key2.txt') as f:
    lines = f.readlines()
    # print('lines', lines)
    for line in lines:
        keys.append(line.split('/')[-1].replace('\n', ''))
    print('Keys', keys)

for bucketKey in keys:
    localfile = '../emberfiles/' + bucketKey 
    print('localfile', localfile)
    download_s3_file(BUCKET_NAME, bucketKey, localfile)

# # Using for loop
# print("Using for loop")
# for keyfile in file1:
# 	count += 1
#     keyfile_list = keyfile.split('/')

# keyobject =  keyfile_list[-1]
# print (f("keyobect: keyobject))
# download_s3_file()