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
from wis2box.env import STORAGE_PUBLIC, URL, STORAGE_SOURCE
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
    def __init__(self, identifier, topic, filepath, geometry=None,
                 wigos_station_identifier=None):

        super().__init__('wis2-notification-message', identifier,
                         topic, filepath, geometry)

        suffix = self.filepath.split('.')[-1]
        try:
            mimetype = DATA_OBJECT_MIMETYPES[suffix]
        except KeyError:
            mimetype = 'application/octet-stream'
        # WIS2 requires us to specify content-encoding
        # options are 'utf-8' or 'base64'
        file_encoding = 'utf-8'
        if suffix in ['bufr4', 'grib2']:
            file_encoding = 'base64'

        # replace storage-source with wis2box-url
        public_file_url = self.filepath.replace(
            f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}', f'{URL}/data'
        )
        self.message = {
            'id': self.identifier,
            'type': 'Feature',
            'version': 'v04',
            'geometry': self.geometry,
            'properties': {
                'data_id': f'{topic}/{self.identifier}',
                'pubtime': self.publish_datetime,
                'content': {
                    'size': self.length,
                    'encoding': file_encoding
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

        if wigos_station_identifier is not None:
            self.message['properties']['wigos_station_identifier'] = wigos_station_identifier  # noqa
            link = {
                'rel': 'via',
                'type': 'text/html',
                'href': f'https://oscar.wmo.int/surface/#/search/station/stationReportDetails/{wigos_station_identifier}'  # noqa
            }
            self.message['links'].append(link)


def gcm() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'messages',
        'type': 'feature',
        'title': 'Data notifications',
        'description': 'Data notifications',
        'keywords': ['wmo', 'wis 2.0'],
        'bbox': [-180, -90, 180, 90],
        'links': ['https://example.org'],
        'id_field': 'id',
        'time_field': 'pubtime',
        'title_field': 'id'
    }
