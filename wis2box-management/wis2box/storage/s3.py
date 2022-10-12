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

import logging
from pathlib import Path
from typing import Any

import boto3

from wis2box.storage.base import StorageBase

LOGGER = logging.getLogger(__name__)


class S3Storage(StorageBase):
    """S3 storage manager"""
    def __init__(self, defs: dict) -> None:

        super().__init__(defs)

        self.client = boto3.client('s3', endpoint_url=self.source,
                                   aws_access_key_id=self.auth['username'],
                                   aws_secret_access_key=self.auth['password'])

    def get(self, identifier: str) -> Any:

        LOGGER.debug(f'Getting object {identifier}')
        data = self.client.get_object(Bucket=self.name, Key=identifier)

        return data['Body'].read()

    def put(self, filepath: Path, identifier: str) -> bool:

        LOGGER.debug(f'Putting file {filepath} to {identifier}')
        self.client.upload_file(filepath, self.name, identifier)

        return True

    def delete(self, identifier: str) -> bool:

        LOGGER.debug(f'Deleting object {identifier}')
        self.client.delete_object(Bucket=self.name, Key=identifier)

        return True

    def __repr__(self):
        return f'<S3Storage ({self.source})>'
