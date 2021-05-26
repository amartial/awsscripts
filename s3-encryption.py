import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import sys

# pip install cryptography

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('s3_encrypt')

def retrieve_cmk(desc):
    """Retrieve an existing KMS CMK based on its description

    :param desc: Description of CMK specified when the CMK was created
    :return Tuple(KeyId, KeyArn) where:
        KeyId: CMK ID
        KeyArn: Amazon Resource Name of CMK
    :return Tuple(None, None) if a CMK with the specified description was
    not found
    """

    # Retrieve a list of existing CMK
    # If more than 100 keys exist, retrieve and process them in batches
    kms_client = boto3.client('kms')
    try:
        response = kms_client.list_keys()
    except ClientError as e:
        logging.error(e)
        return None, None

    done = False
    while not done:
        for cmk in response['Keys']:
            # Get info about the key, including its description
            try:
                key_info = kms_client.describe_key(KeyId=cmk['KeyArn'])
            except ClientError as e:
                logging.error(e)
                return None, None

            # Is this the key we're looking for?
            if key_info['KeyMetadata']['Description'] == desc:
                return cmk['KeyId'], cmk['KeyArn']

        # Are there more keys to retrieve?
        if not response['Truncated']:
            # No, the CMK was not found
            logging.debug('A CMK with the specified description was not found')
            done = True
        else:
            # Yes, retrieve another batch
            try:
                response = kms_client.list_keys(Marker=response['NextMarker'])
            except ClientError as e:
                logging.error(e)
                return None, None

    # All existing CMKs were checked and the desired key was not found
    return None, None

def create_cmk(desc='Customer Master Key'):
    """Create a KMS Customer Master Key

    The created CMK is a Customer-managed key stored in AWS KMS.

    :param desc: key description
    :return Tuple(KeyId, KeyArn) where:
        KeyId: AWS globally-unique string ID
        KeyArn: Amazon Resource Name of the CMK
    :return Tuple(None, None) if error
    """

    # Create CMK
    kms_client = boto3.client('kms')
    try:
        response = kms_client.create_key(Description=desc)
    except ClientError as e:
        logging.error(e)
        return None, None

    # Return the key ID and ARN
    return response['KeyMetadata']['KeyId'], response['KeyMetadata']['Arn']

def create_data_key(cmk_id, key_spec='AES_256'):
    """Generate a data key to use when encrypting and decrypting data

    :param cmk_id: KMS CMK ID or ARN under which to generate and encrypt the
    data key.
    :param key_spec: Length of the data encryption key. Supported values:
        'AES_128': Generate a 128-bit symmetric key
        'AES_256': Generate a 256-bit symmetric key
    :return Tuple(EncryptedDataKey, PlaintextDataKey) where:
        EncryptedDataKey: Encrypted CiphertextBlob data key as binary string
        PlaintextDataKey: Plaintext base64-encoded data key as binary string
    :return Tuple(None, None) if error
    """

    # Create data key
    kms_client = boto3.client('kms')
    try:
        response = kms_client.generate_data_key(KeyId=cmk_id, KeySpec=key_spec)
    except ClientError as e:
        logging.error(e)
        return None, None

    # Return the encrypted and plaintext data key
    return response['CiphertextBlob'], base64.b64encode(response['Plaintext'])



def decrypt_data_key(data_key_encrypted):
    """Decrypt an encrypted data key

    :param data_key_encrypted: Encrypted ciphertext data key.
    :return Plaintext base64-encoded binary data key as binary string
    :return None if error
    """

    # Decrypt the data key
    kms_client = boto3.client('kms')
    try:
        response = kms_client.decrypt(CiphertextBlob=data_key_encrypted)
    except ClientError as e:
        logging.error(e)
        return None

    # Return plaintext base64-encoded binary data key
    return base64.b64encode((response['Plaintext']))

def decrypt_file(filename):
    """Decrypt a file encrypted by encrypt_file()

    The encrypted file is read from <filename>.encrypted
    The decrypted file is written to <filename>.decrypted

    :param filename: File to decrypt
    :return: True if file was decrypted. Otherwise, False.
    """

    # Read the encrypted file into memory
    try:
        with open(filename + '.encrypted', 'rb') as file:
            file_contents = file.read()
    except IOError as e:
        logging.error(e)
        return False

    # The first NUM_BYTES_FOR_LEN bytes contain the integer length of the
    # encrypted data key.
    # Add NUM_BYTES_FOR_LEN to get index of end of encrypted data key/start
    # of encrypted data.
    data_key_encrypted_len = int.from_bytes(file_contents[:NUM_BYTES_FOR_LEN],
                                            byteorder='big') \
                             + NUM_BYTES_FOR_LEN
    data_key_encrypted = file_contents[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    # Decrypt the data key before using it
    data_key_plaintext = decrypt_data_key(data_key_encrypted)
    if data_key_plaintext is None:
        return False

    # Decrypt the rest of the file
    f = Fernet(data_key_plaintext)
    file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    # Write the decrypted file contents
    try:
        with open(filename + '.decrypted', 'wb') as file_decrypted:
            file_decrypted.write(file_contents_decrypted)
    except IOError as e:
        logging.error(e)
        return False

    # The same security issue described at the end of encrypt_file() exists
    # here, too, i.e., the wish to wipe the data_key_plaintext value from
    # memory.
    return True

def encrypt_file(filename, cmk_id):
    """Encrypt a file using an AWS KMS CMK

    A data key is generated and associated with the CMK.
    The encrypted data key is saved with the encrypted file. This enables the
    file to be decrypted at any time in the future and by any program that
    has the credentials to decrypt the data key.
    The encrypted file is saved to <filename>.encrypted
    Limitation: The contents of filename must fit in memory.

    :param filename: File to encrypt
    :param cmk_id: AWS KMS CMK ID or ARN
    :return: True if file was encrypted. Otherwise, False.
    """

    # Read the entire file into memory
    try:
        with open(filename, 'rb') as file:
            file_contents = file.read()
    except IOError as e:
        logging.error(e)
        return False

    # Generate a data key associated with the CMK
    # The data key is used to encrypt the file. Each file can use its own
    # data key or data keys can be shared among files.
    # Specify either the CMK ID or ARN
    data_key_encrypted, data_key_plaintext = create_data_key(cmk_id)
    if data_key_encrypted is None:
        return False
    logging.info('Created new AWS KMS data key')

    # Encrypt the file
    f = Fernet(data_key_plaintext)
    file_contents_encrypted = f.encrypt(file_contents)

    # Write the encrypted data key and encrypted file contents together
    try:
        with open(filename + '.encrypted', 'wb') as file_encrypted:
            file_encrypted.write(len(data_key_encrypted).to_bytes(NUM_BYTES_FOR_LEN,
                                                                  byteorder='big'))
            file_encrypted.write(data_key_encrypted)
            file_encrypted.write(file_contents_encrypted)
    except IOError as e:
        logging.error(e)
        return False

    # For the highest security, the data_key_plaintext value should be wiped
    # from memory. Unfortunately, this is not possible in Python. However,
    # storing the value in a local variable makes it available for garbage
    # collection.
    return True


s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

response = s3client.list_buckets()

my_kms_key_id = "arn:aws:kms:us-east-1:180223572663:key/e31a0a29-832e-4145-8b8c-b19cbc984d2a"

# print('respose', response)

for bucket in response['Buckets']:
  #print('bucket', bucket)
  try:
    # enc = s3client.get_bucket_encryption(Bucket=bucket['Name'])
    # rules = enc['ServerSideEncryptionConfiguration']['Rules']
    # print('Bucket: %s, Encryption: %s' % (bucket['Name'], rules))
    my_bucket = s3resource.Bucket(bucket['Name'])
    print('my_bucket', my_bucket)
    i = 0
    for file in my_bucket.objects.all():
        # print('encryption: ', file.server_side_encryption)
        my_file = s3resource.Object(bucket['Name'], file.key)
        print('encryption: ', my_file.key, ' clef: ', my_file.server_side_encryption, ' kms_key_id: ', my_file.ssekms_key_id)
        # if my_file.server_side_encryption is None:
        #     print('encryption process')

        if my_file.server_side_encryption is None:
            LOGGER.debug('Encrypting object: %s', my_file.key)
            copy_source = {
                'Bucket': bucket['Name'],
                'Key': my_file.key
            }

            resp = s3client.copy_object(
                Bucket=bucket['Name'],
                CopySource=copy_source,
                Key=my_file.key,
                ServerSideEncryption='aws:kms'
            )

            i += 1
        if i == 1:  # Contrainte pour crypter seulement un fichier par dossier sur aws s3
            break
        # my_file.
        # encrypt_file("s3://" + bucket['Name'] + "/" + my_file.key, my_kms_key_id)

  except ClientError as e:
    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
      print('Bucket: %s, no server-side encryption' % (bucket['Name']))
      continue
    else:
      print("Bucket: %s, unexpected error: %s" % (bucket['Name'], e))
      continue


