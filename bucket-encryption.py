import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

# pip install cryptography

s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

response = s3client.list_buckets()

for bucket in response['Buckets']:
  print('bucket: ', bucket['Name'])
  try:
    enc = s3client.get_bucket_encryption(Bucket=bucket['Name'])
    rules = enc['ServerSideEncryptionConfiguration']['Rules']
    print('Bucket Encrypted: %s' % (rules))

  except ClientError as e:
    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
      print('Bucket: %s, no server-side encryption' % (bucket['Name']))
      try:
        response = s3client.get_bucket_encryption(Bucket=bucket['Name'])
        print('res', response)
      except s3client.exceptions.ClientError as e2:
          if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            response = s3client.put_bucket_encryption(Bucket=bucket['Name'], ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}},]})
          else:
              print("Unexpected error: %s" % e2)
    else:
    #   print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))
      continue


