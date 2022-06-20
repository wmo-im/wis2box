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

LOGGER = logging.getLogger(__name__)


class SecureHashAlgorithms(Enum):
    SHA512 = 'sha512'
    MD5 = 'md5'


class PubSubMessage:
    """
    Generic message class
    """

    def __init__(self, type_: str, filepath: Path) -> None:
        """
        Initializer

        :param type_: message type
        :param filepath: `Path` of file

        :returns: `wis2box.pubsub.message.PubSubMessage` message object
        """

        self.type = type_
        self.filepath = filepath
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
        return json.dumps(self.message)

    def _generate_checksum(self, algorithm: SecureHashAlgorithms) -> str:
        """
        Generate a checksum of message file

        :param algorithm: secure hash algorithm (md5, sha512)

        :returns: `str` of hexdigest
        """

        sh = getattr(hashlib, algorithm)()

        with self.filepath.open('rb') as fh:
            while True:
                chunk = fh.read(sh.block_size)
                if not chunk:
                    break
                sh.update(chunk)

        return sh.hexdigest()


class Sarracenia_v03Message(PubSubMessage):
    def __init__(self, filepath):
        super().__init__('sarracenia-v03', filepath)

        self.message['relPath'] = self.filepath
        self.message['baseUrl'] = '/'

    def prepare(self):
        self.message['pubTime'] = datetime.now().strftime('%Y%m%dT%H%M%S.%f')
        filepath = Path(self.message['relPath']) / self.message['baseUrl']
        self.message['size'] = filepath.stat().st_size
        self.message['integrity'] = {
            'method': 'sha512',
            'value': self._generate_checksum('sha512'),
        }


class WISNotificationMessage(PubSubMessage):
    def __init__(self):
        super().__init__('wis2-notification-message')
