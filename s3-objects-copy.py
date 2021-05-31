import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

parser = argparse.ArgumentParser()
parser.add_argument('--bucket-source', action='store', dest='bucket_source', default=False)
parser.add_argument('--key-source', action='store', dest='key_source', default=False)
parser.add_argument('--bucket-dest', action='store', dest='bucket_dest', default=False)
parser.add_argument('--key-dest', action='store', dest='key_dest', default=False)
parser.add_argument('--debug', action='store_true', dest='debug', default=False)


args = parser.parse_args()

print('args', args)

# Set up Debug Logging
if args.debug:
    LOGGER.setLevel(logging.DEBUG)

error = False

if not args.bucket_source:
    print('Please ! specify bucket_source')
    error = True

if not args.key_source:
    print('Please ! specify key_source')
    error = True

if not args.bucket_dest:
    print('Please ! specify bucket_dest')
    error = True

if not args.key_dest:
    print('Please ! specify key_dest')
    error = True

if error:
    print('python s3-objects-copy.py --bucket-source=bucket_source --key-source=key_source --bucket-dest=bucket_dest --key-dest=key_dest')

if args.bucket_source and args.key_source and args.bucket_dest and args.key_dest:
    print('Executing s3 copy ...')
    copy_source = {
        'Bucket': args.bucket_source,
        'Key': args.key_source
    }
    try:
      source_list = args.key_source.split('/')
      dest_list = args.key_dest.split('/')
      key_list = dest_list[:-1] + source_list
      key_string = '/'.join(key_list)
      print('destination: ', key_string)
      # s3resource.meta.client.copy(copy_source, args.bucket_dest, key_string)
      copy_source = {
        'Bucket': args.bucket_source,
        'Key': args.key_source
      }
      bucket = s3resource.Bucket(args.bucket_dest)
      bucket.copy(copy_source, key_string)
      print('Succes copy file')

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print('Bucket not found: ')
        else:
            print("Unexpected error: %s" % e)
