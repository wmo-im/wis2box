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

from ast import Bytes
from enum import Enum
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


class StorageTypes(Enum):
    FS = 'fs'
    minio = 'minio'


class StorageBase:
    """Abstract storage manager"""
    def __init__(self, storage_type: StorageTypes, source: str,
                 name: str = None, auth: dict = None) -> None:
        """
        DataSource initializer

        :param storage_type: type of storage
        :param source: URL of storage service, or basepath of filesystem
        :param name: bucket or container name (can be None if not applicable)
        :param auth: `dict` of auth parameters (specific to provider)

        :returns: `None`
        """

        self.storage_type = storage_type
        self.source = source
        self.name = name
        self.auth = auth

    def get(self, identifier: str) -> Any:
        """
        Access data source from storage

        :param identifier: `str` of data source identifier

        :returns: object result
        """

        raise NotImplementedError()

    def put(self, filepath: Path, identifier: str) -> bool:
        """
        Access data source from storage

        :param filepath: `Path` of file to upload
        :param identifier: `str` of data source identifier

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

    def __repr__(self):
        return f'<StorageBase ({self.source})>'
