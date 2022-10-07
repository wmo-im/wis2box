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

from datetime import datetime
from enum import Enum
import json
import hashlib
import logging
from pathlib import Path

from wis2box.util import json_serial
from wis2box.storage import get_data

LOGGER = logging.getLogger(__name__)


class SecureHashAlgorithms(Enum):
    SHA512 = 'sha512'
    MD5 = 'md5'


DATA_OBJECT_MIMETYPES = {
    'bufr4': 'application/x-bufr',
    'grib2': 'application/x-grib2',
    'geojson': 'application/json'
}


class PubSubMessage:
    """
    Generic message class
    """

    def __init__(self, type_: str, identifier: str, topic: str, filepath: str,
                 geometry: dict = None,
                 wigos_station_identifier: str = None) -> None:
        """
        Initializer

        :param type_: message type
        :param identifier: identifier
        :param topic: topic
        :param filepath: `Path` of file
        :param geometry: `dict` of GeoJSON geometry object
        :param wigos_station_identifier: WSI associated with the data

        :returns: `None`
        """

        self.type = type_
        self.identifier = identifier
        self.filepath = filepath
        self.geometry = geometry
        self.publish_datetime = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
        self.checksum_type = SecureHashAlgorithms.SHA512.value
        # needs to get bytes to calc checksum and get length
        filebytes = None
        if isinstance(self.filepath, Path):
            with self.filepath.open('rb') as fh:
                filebytes = fh.read()
        else:
            filebytes = get_data(filepath)
        self.length = len(filebytes)
        self.checksum_value = self._generate_checksum(filebytes, self.checksum_type) # noqa
        self.message = {}

    def prepare(self):
        """
        Prepare message before dumping

        :returns: `None`
        """

        raise NotImplementedError()

    def dumps(self) -> str:
        """
        Return string representation of message

        :returns: `str` of message content
        """

        if self.message:
            return json.dumps(self.message, default=json_serial)
        else:
            return json.dumps(self, default=json_serial)

    def _generate_checksum(self, bytes, algorithm: SecureHashAlgorithms) -> str:  # noqa
        """
        Generate a checksum of message file

        :param algorithm: secure hash algorithm (md5, sha512)

        :returns: `tuple` of hexdigest and length
        """

        sh = getattr(hashlib, algorithm)()
        sh.update(bytes)
        return sh.hexdigest()
