###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

from io import BytesIO
import json
import logging
from typing import Any
from urllib.parse import urlparse

from minio import Minio
from minio import error as minio_error
from minio.notificationconfig import NotificationConfig, QueueConfig

from wis2box.storage.base import PolicyTypes, StorageBase

LOGGER = logging.getLogger(__name__)


# default policies

def readonly_policy(name):
    return {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': {'AWS': '*'},
            'Action': ['s3:GetBucketLocation', 's3:ListBucket'],
            'Resource': f'arn:aws:s3:::{name}',
        }, {
            'Effect': 'Allow',
            'Principal': {'AWS': '*'},
            'Action': 's3:GetObject',
            'Resource': f'arn:aws:s3:::{name}/*',
        }]
    }


def readwrite_policy(name):
    return {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': {'AWS': '*'},
            'Action': [
                's3:GetBucketLocation',
                's3:ListBucket',
                's3:ListBucketMultipartUploads',
            ],
            'Resource': f'arn:aws:s3:::{name}',
        }, {
            'Effect': 'Allow',
            'Principal': {'AWS': '*'},
            'Action': [
                's3:GetObject',
                's3:PutObject',
                's3:DeleteObject',
                's3:ListMultipartUploadParts',
                's3:AbortMultipartUpload',
            ],
            'Resource': f'arn:aws:s3:::{name}/*',
        }]
    }


class MinIOStorage(StorageBase):
    """MinIO storage manager"""
    def __init__(self, defs: dict) -> None:

        super().__init__(defs)

        is_secure = False

        urlparsed = urlparse(self.source)

        if self.source.startswith('https://'):
            is_secure = True

        self.client = Minio(endpoint=urlparsed.netloc,
                            access_key=self.auth['username'],
                            secret_key=self.auth['password'],
                            secure=is_secure)

    def setup(self):
        LOGGER.debug(f'Creating buckets at MinIO endpoint {self.source}')
        self.create_bucket(bucket_policy=self.policy)

    def set_policy(self, bucket_policy: PolicyTypes = 'private'):
        LOGGER.debug(f'Set bucket_policy={bucket_policy} on {self.name}')
        if bucket_policy == 'readonly':
            self.client.set_bucket_policy(
                self.name, json.dumps(readonly_policy(self.name)))
        elif bucket_policy == 'readwrite':
            self.client.set_bucket_policy(
                self.name, json.dumps(readwrite_policy(self.name)))
        elif bucket_policy == 'private':
            self.client.delete_bucket_policy(self.name)
        else:
            LOGGER.warning(f'bucket_policy={bucket_policy} unknown')

    def create_bucket(self, bucket_policy: PolicyTypes = 'private'):
        # create bucket if not exist
        found = self.client.bucket_exists(self.name)
        if not found:
            self.client.make_bucket(self.name)
        else:
            LOGGER.info(f'Bucket {self.name} already exists')
        self.set_policy(bucket_policy)
        # add notifications to be sent to local-broker
        config = NotificationConfig(
            queue_config_list=[
                QueueConfig(
                    'arn:minio:sqs::WIS2BOX:mqtt',
                    ['s3:ObjectCreated:*'],
                    config_id='1'
                )
            ]
        )
        LOGGER.debug(f'Adding notification config {config}')
        self.client.set_bucket_notification(self.name, config)

    def exists(self, identifier: str) -> bool:
        LOGGER.debug(f'Checking if object {identifier} exists')
        try:
            # Attempt to get object info to check if it exists
            self.client.stat_object(bucket_name=self.name, object_name=identifier) # noqa
            return True  # Object exists
        except minio_error.S3Error as err:
            if err.code == 'NoSuchKey':
                LOGGER.debug(err)
                return False
            else:
                LOGGER.error(err)
                raise err
        except Exception as err:
            LOGGER.error(err)
            raise err

    def get(self, identifier: str) -> Any:

        LOGGER.debug(f'Getting object {identifier} from bucket={self.name}')
        # Get data of an object.
        try:
            response = self.client.get_object(
                self.name, object_name=identifier)
            data = response.data
            response.close()
            response.release_conn()
        except Exception as err:
            LOGGER.error(err)
            raise err

        return data

    def put(self, data: bytes, identifier: str,
            content_type: str = 'application/octet-stream') -> bool:

        LOGGER.debug(f'Putting data as object={identifier}')
        self.client.put_object(bucket_name=self.name, object_name=identifier,
                               content_type=content_type,
                               data=BytesIO(data), length=-1,
                               part_size=10*1024*1024)

        return True

    def delete(self, identifier: str) -> bool:

        LOGGER.debug(f'Deleting object {identifier}')
        self.client.remove_object(self.name, identifier)

        return True

    def list_objects(self, prefix: str) -> list:
        LOGGER.debug(f'list identifiers starting with {prefix}')
        objects = []
        for object in self.client.list_objects(self.name, prefix, True): # noqa
            objects.append({
                'filename': object.object_name.split('/')[-1],
                'fullpath': f'{self.source}/{self.name}/{object.object_name}',
                'last_modified': object.last_modified,
                'size': object.size,
                'basedir': object.object_name.split('/')[0],
            })
        return objects

    def __repr__(self):
        return f'<MinioStorage ({self.source})>'
