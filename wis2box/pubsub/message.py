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
from wis2box.env import URL, STORAGE_SOURCE
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

    def __init__(self, type_: str, identifier: str, filepath: str,
                 geometry: dict = None) -> None:
        """
        Initializer

        :param type_: message type
        :param identifier: identifier
        :param geometry: `dict` of GeoJSON geometry object
        :param filepath: `Path` of file

        :returns: `wis2box.pubsub.message.PubSubMessage` message object
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


class WISNotificationMessage(PubSubMessage):
    def __init__(self, identifier, filepath, geometry=None):
        super().__init__('wis2-notification-message', identifier,
                         filepath, geometry)

        suffix = self.filepath.split('.')[-1]

        try:
            mimetype = DATA_OBJECT_MIMETYPES[suffix]
        except KeyError:
            mimetype = 'application/octet-stream'
        # replace storage-source with wis2box-url
        public_file_url = self.filepath.replace(STORAGE_SOURCE, URL)
        self.message = {
            'id': self.identifier,
            'type': 'Feature',
            'version': 'v04',
            'geometry': self.geometry,
            'properties': {
                'pubTime': self.publish_datetime,
                'content': {
                    'length': self.length
                },
                'integrity': {
                    'method': self.checksum_type,
                    'value': self.checksum_value
                }
            },
            'links': [{
                'rel': 'canonical',
                'type': mimetype,
                'href': public_file_url
            }]
        }


def generate_collection_metadata() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'messages',
        'type': 'collection',
        'title': 'Data notifications',
        'description': 'Data notifications',
        'keywords': ['wmo', 'wis 2.0'],
        'extents': {
            'spatial': {
                'bbox': [-180, -90, 180, 90],
                'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
            }
        },
        'id_field': 'id',
        'time_field': 'pubTime',
        'title_field': 'id',
        'providers': [],
        'links': []
    }
