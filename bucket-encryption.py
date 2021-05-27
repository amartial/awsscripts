import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

# pip install cryptography

# logging.basicConfig(level=logging.INFO)
# LOGGER = logging.getLogger('s3_encrypt')
s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

def default_bucket_encryption_sse_cmk_set(s3_client, bucket_name, kms_master_key_id):
  s3_client.put_bucket_encryption(
    bucket_name,
    {
      'rules': [
        {
          'apply_server_side_encryption_by_default': {
            'sse_algorithm': 'aws:kms',
            'kms_master_key_id': kms_master_key_id
          }
        }
      ]
    }
  )
  return true



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
      # bucketResource = s3resource.Bucket(bucket['Name'])
      # bucketResource.putBucketEncryption()
      # res = default_bucket_encryption_sse_cmk_set(s3client, bucket['Name'], 'e31a0a29-832e-4145-8b8c-b19cbc984d2a')
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


