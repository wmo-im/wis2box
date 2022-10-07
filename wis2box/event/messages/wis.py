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
import re

from wis2box.env import STORAGE_PUBLIC, STORAGE_SOURCE, URL
from wis2box.event.messages.base import PubSubMessage, DATA_OBJECT_MIMETYPES

LOGGER = logging.getLogger(__name__)


class WISNotificationMessage(PubSubMessage):
    def __init__(self, identifier, topic, filepath, geometry=None):
        super().__init__(
            'wis2-notification-message', identifier, topic, filepath, geometry
        )

        suffix = self.filepath.split('.')[-1]

        try:
            mimetype = DATA_OBJECT_MIMETYPES[suffix]
        except KeyError:
            mimetype = 'application/octet-stream'
        # replace storage-source with wis2box-url
        public_file_url = self.filepath.replace(
            f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}', f'{URL}/data'
        )
        wsi = re.match(r'^WIGOS_(\d-\d+-\d+-\w+)_.*$', identifier).group(1)
        self.message = {
            'id': self.identifier,
            'type': 'Feature',
            'version': 'v04',
            'geometry': self.geometry,
            'properties': {
                'data-id': f'{topic}/{self.identifier}',
                'pubTime': self.publish_datetime,
                'wigos_station_identifier': wsi,
                'content': {'length': self.length},
                'integrity': {
                    'method': self.checksum_type,
                    'value': self.checksum_value
                }
            },
            'links': [
                {'rel': 'canonical', 'type': mimetype, 'href': public_file_url}
            ]
        }
