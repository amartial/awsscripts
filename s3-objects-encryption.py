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

response = s3client.list_buckets()

for bucket in response['Buckets']:
  print('bucket: ', bucket['Name'])
  try:
    enc = s3client.get_bucket_encryption(Bucket=bucket['Name'])
    rules = enc['ServerSideEncryptionConfiguration']['Rules']
    print('Bucket Encrypted: %s' % (rules))
    bucketResource = s3resource.Bucket(bucket['Name'])
    # print('bucketResource', bucketResource)
    i = 0
    for objectSummary in bucketResource.objects.all():
        objectResource = s3resource.Object(bucket['Name'], objectSummary.key)
        # print('encryption: ', objectResource.key, ' clef: ', objectResource.server_side_encryption, ' kms_key_id: ', objectResource.ssekms_key_i**************.*;:server_side_encryption is None:
        if objectResource.server_side_encryption is None:
            print("Cryptage de l'objet: ", objectResource.key)
            copy_source = {
                'Bucket': bucket['Name'],
                'Key': objectResource.key
            }

            resp = s3client.copy_object(
                Bucket=bucket['Name'],
                CopySource=copy_source,
                Key=objectResource.key,
                ServerSideEncryption='aws:kms'
            )

            # print("Resultat du cryptage: ", resp)

            i += 1
        if i == 1:  # Contrainte pour crypter seulement un fichier par dossier sur aws s3
            break
        # my_file.
        # encrypt_file("s3://" + bucket['Name'] + "/" + my_file.key, my_kms_key_id)

  except ClientError as e:
    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
    #   print('Bucket: %s, no server-side encryption' % (bucket['Name']))
      continue
    else:
    #   print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))
      continue


