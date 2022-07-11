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
from typing import Any

from wis2box.env import (STORAGE_TYPE, STORAGE_SOURCE,
                         STORAGE_USERNAME, STORAGE_PASSWORD)
from wis2box.plugin import load_plugin


LOGGER = logging.getLogger('__name__')


def get_data(path: str) -> Any:
    """
    Get data from storage

    :param path: path of object/file

    :returns: content of object/file
    """

    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD}
    }

    LOGGER.debug('Connecting to storage: {defs}')
    storage = load_plugin('storage', defs)

    identifier = storage_path.replace(name, '')

    LOGGER.debug(f'Fetching {identifier}')
    return storage.get(identifier)
