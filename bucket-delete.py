import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

parser = argparse.ArgumentParser()
parser.add_argument('--bucket-name', action='store', dest='bucket_name', default=False)
parser.add_argument('--debug', action='store_true', dest='debug', default=False)

args = parser.parse_args()
# print('args', args)

# Set up Debug Logging
if args.debug:
    LOGGER.setLevel(logging.DEBUG)

error = False

if not args.bucket_name:
    print('Please ! specify bucket_name')
    error = True

if error:
    print('python bucket-delete.py --bucket-name=bucketname')

if args.bucket_name:
    print('Deleting s3 bucket ...')

    try:
        bucketResource = s3resource.Bucket(args.bucket_name)
        to_delete_keys = [elt.key for elt in bucketResource.objects.all()]
        key_counter = 0
        to_delete = []
        while key_counter <= 999 and key_counter < len(to_delete_keys):
            
            to_delete.append(
            {
                'Key': to_delete_keys[key_counter],
                # 'VersionId': 'string',
                # 'DeleteMarker': True|False,
                # 'DeleteMarkerVersionId': 'string'
            }
            )
            print('to_delete', to_delete)
            if len(to_delete_keys) % 999 == 0:
                delete = {
                    'Objects': to_delete,
                    'Quiet': False
                }
                response = bucketResource.delete_objects(Bucket=args.bucket_name, Delete=delete)
                to_delete = []
                print('delete response ', response)
            key_counter += 1
        print(key_counter, len(to_delete_keys))
        if key_counter == len(to_delete_keys):
            delete = {
                'Objects': to_delete,
                'Quiet': False
            }
            response = bucketResource.delete_objects(Bucket=args.bucket_name, Delete=delete)
            print('delete response2 ', response)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print('Bucket not found: ', bucket)
        else:
            print("Unexpected error: %s" % e)
