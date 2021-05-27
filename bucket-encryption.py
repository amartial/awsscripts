import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys
import json

s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

bucketList = []

if len(sys.argv[1:]) == 0:
  print("There is no specified buckets to encrypt:\n\t - 'python bucket-encryption.py --all' To run on all your aws s3 buckets. \n\t - 'python bucket-encryption.py bucket1 bucket2 ...' To run on specifics buckets")
elif len(sys.argv[1:]) == 1 and sys.argv[1] == '--bucketlist=all':
  buckets = s3client.list_buckets()['Buckets']
  bucketList = [bucket['Name'] for bucket in buckets]
else:
  try:
    argument = sys.argv[1].split('=')[1]
    restarg = sys.argv[2:]
    listargs = [argument]+restarg
    stringlistarg = ','.join(listargs)
    stringlistarg = stringlistarg.replace('[', '').replace(']', '').replace(',,', ',')
    print('stringlistarg', stringlistarg)
    bucketList = stringlistarg.split(',')
  except:
    print('There is a problem with your argument')

print('Bucket list: ', bucketList)

for bucket in bucketList:
  print('bucket: ', bucket)
  try:
    enc = s3client.get_bucket_encryption(Bucket=bucket)
    rules = enc['ServerSideEncryptionConfiguration']['Rules']
    print('Bucket Encrypted: %s' % (rules))

  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucket':
      print('Bucket not found: ', bucket)
    elif e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
      print('Encrypting bucket: %s' % (bucket))
      try:
        response = s3client.get_bucket_encryption(Bucket=bucket)
        print('res', response)
      except s3client.exceptions.ClientError as e2:
          if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            response = s3client.put_bucket_encryption(Bucket=bucket, ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}},]})
          else:
              print("Unexpected error: %s" % e2)
    else:
    #   print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))
      continue


