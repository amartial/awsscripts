import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

parser = argparse.ArgumentParser()
parser.add_argument('--bucket-name', action='store', dest='bucket_name', default=False)
parser.add_argument('--bucket-object-key', action='store', dest='bucket_object_key', default=False)
parser.add_argument('--debug', action='store_true', dest='debug', default=False)


args = parser.parse_args()

print('args', args, args.bucket_name)

# Set up Debug Logging
if args.debug:
    LOGGER.setLevel(logging.DEBUG)

error = False

if not args.bucket_name:
    print('Please ! specify bucket_name')
    error = True

if not args.bucket_object_key:
    print('Please ! specify bucket object key')
    error = True

if error:
    print('s3-objects-delete.py --bucket-name=bucketname --bucket-object-key=bucket_object_key')

if args.bucket_name and args.bucket_object_key:
    print('Deleting s3 bucket object ...')

    try:
        s3resource.Object(args.bucket_name, args.bucket_object_key).delete()
        print(args.bucket_object_key, ' deleted')

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print('Bucket not found: ', bucket)
        else:
            print("Unexpected error: %s" % e)
