# test- script to copy data to minio to test ingest based on events
# TODO makes this a proper executable, or just for test ?

import glob
import sys
from minio import Minio

local_path = sys.argv[1]
minio_path = sys.argv[2]

filepaths = glob.glob(local_path)
if len(filepaths) == 0:
    print(f'No files found for pattern={local_path}')

S3_ENDPOINT = 'http://localhost:9000'
S3_USER = 'minio'
S3_PASSWORD = 'minio123'
S3_BUCKET_INCOMING = 'wis2box-incoming'

if S3_ENDPOINT != '':
    is_secure = False
    endpoint = ''
    if S3_ENDPOINT.startswith('https://'):
        is_secure = True
        endpoint = S3_ENDPOINT.replace('https://', '')
    else:
        endpoint = S3_ENDPOINT.replace('http://', '')
    client = Minio(
        endpoint=endpoint,
        access_key=S3_USER,
        secret_key=S3_PASSWORD,
        secure=is_secure)
    for filepath in filepaths:
        filepath = filepath.replace('\\', '/')
        identifier = minio_path+'/'+filepath.split('/')[-1]
        print(f"Put into {S3_BUCKET_INCOMING} : {filepath} as {identifier}")
        client.fput_object(S3_BUCKET_INCOMING, identifier, filepath)
else:
    print('S3_ENDPOINT is not defined')
    raise Exception
