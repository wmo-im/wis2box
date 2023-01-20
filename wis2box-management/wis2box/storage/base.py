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

from enum import Enum
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class StorageTypes(Enum):
    FS = 'fs'
    S3 = 'S3'


class PolicyTypes(Enum):
    readonly = 'readonly'
    readwrite = 'readwrite'
    private = 'private'


class StorageBase:
    """Abstract storage manager"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of storage parameters
                     (storage_type, source, name, auth, policy)
        """

        self.storage_type = defs.get('storage_type')
        self.source = defs.get('source')
        self.name = defs.get('name')
        self.auth = defs.get('auth')
        self.policy = defs.get('policy')

    def setup(self) -> bool:
        """
        Run setup harness specific to storage

        :returns: `bool` of setup result
        """

        raise NotImplementedError()

    def get(self, identifier: str) -> Any:
        """
        Access data source from storage

        :param identifier: `str` of data source identifier

        :returns: object result
        """

        raise NotImplementedError()

    def put(self, data: bytes, identifier: str) -> bool:
        """
        Access data source from storage

        :param data: bytes of file to upload
        :param identifier: `str` of data dest identifier

        :returns: `bool` of put result
        """

        raise NotImplementedError()

    def put_bytes(self, data: bytes, identifier: str) -> bool:
        """
        Access data source from storage

        :param data: `bytes` of file to upload
        :param identifier: `str` of data source identifier

        :returns: `bool` of put result
        """

        raise NotImplementedError()

    def delete(self, identifier: str) -> bool:
        """
        Delete data source from storage

        :param identifier: `str` of data source identifier

        :returns: `bool` of put result
        """

        raise NotImplementedError()

    def list_objects(self, prefix: str) -> list:
        """
        List objects in storage starting with prefix

        :param 'str' prefix

        :returns: list of 'str'-objects
        """

    def __repr__(self):
        return f'<StorageBase ({self.source})>'
