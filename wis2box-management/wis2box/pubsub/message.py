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

import base64
from datetime import datetime
from enum import Enum
import json
import hashlib
import logging
from pathlib import Path
import uuid

from wis2box import __version__
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

    def __init__(self, type_: str, identifier: str, filepath: str,
                 datetime_: datetime, geometry: dict = None) -> None:
        """
        Initializer

        :param type_: message type
        :param identifier: identifier
        :param filepath: `Path` of file
        :param datetime_: `datetime` object of temporal aspect of data
        :param geometry: `dict` of GeoJSON geometry object

        :returns: `wis2box.pubsub.message.PubSubMessage` message object
        """

        self.filebytes = None

        self.type = type_
        self.identifier = identifier
        self.filepath = filepath
        self.geometry = geometry
        self.datetime = datetime_.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.publish_datetime = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
        self.checksum_type = SecureHashAlgorithms.SHA512.value
        # needs to get bytes to calc checksum and get length
        if isinstance(self.filepath, Path):
            with self.filepath.open('rb') as fh:
                self.filebytes = fh.read()
        else:
            self.filebytes = get_data(filepath)
        self.length = len(self.filebytes)
        self.checksum_value = self._generate_checksum(
            self.filebytes, self.checksum_type)
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
        return base64.b64encode(sh.digest()).decode()


class WISNotificationMessage(PubSubMessage):
    def __init__(self, identifier: str, metadata_id: str, filepath: str,
                 datetime_: str, geometry=None,
                 wigos_station_identifier=None, gts: dict = None,
                 operation: str = 'create') -> None:

        super().__init__('wis2-notification-message', identifier,
                         filepath, datetime_, geometry)

        data_id = f'{self.identifier}'

        if '/metadata' in filepath:
            mimetype = 'application/geo+json'
        else:
            suffix = self.filepath.split('.')[-1]
            mimetype = DATA_OBJECT_MIMETYPES.get(suffix,
                'application/octet-stream')  # noqa

        LOGGER.debug(f'media type: {mimetype}')

        # replace storage source with wis2box URL
        public_file_url = self.filepath.replace(
            f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}', f'{URL}/data'
        )

        if self.datetime is None:
            LOGGER.warning('Missing data datetime')

        links = [{
                'rel': 'canonical',
                'type': mimetype,
                'href': public_file_url,
                'length': self.length
        }]
        if operation == 'update':
            links.append({
                'rel': 'update',
                'type': mimetype,
                'href': public_file_url,
                'length': self.length
            })

        self.message = {
            'id': str(uuid.uuid4()),
            'type': 'Feature',
            'conformsTo': ['http://wis.wmo.int/spec/wnm/1/conf/core'],
            'geometry': self.geometry,
            'properties': {
                'data_id': data_id,
                'datetime': self.datetime,
                'pubtime': self.publish_datetime,
                'integrity': {
                    'method': self.checksum_type,
                    'value': self.checksum_value
                }
            },
            'links': links,
            'generated-by': f'wis2box {__version__}'
        }

        if metadata_id is not None:
            self.message['properties']['metadata_id'] = metadata_id

        # if gts-dictionary is provided, include it in the message properties
        if gts is not None:
            self.message['properties']['gts'] = gts

        if self.length < 4096:
            LOGGER.debug('Including data inline via properties.content')
            content_value = base64.b64encode(self.filebytes)

            self.message['properties']['content'] = {
                'encoding': 'base64',
                'value': content_value,
                'size': self.length
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
