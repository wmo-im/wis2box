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

from wis2node.api.config.base import BaseConfig
from wis2node.env import (API_BACKEND_TYPE, API_BACKEND_HOST,
                          API_BACKEND_PORT, API_CONFIG)
from wis2node.util import yaml_dump, yaml_load

LOGGER = logging.getLogger(__name__)


class PygeoapiConfig(BaseConfig):
    """Abstract API config"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
                     (config)
        """

        super().__init__(defs)

    def add_collection(self, meta: str) -> bool:
        """
        Add a collection

        :param meta: `dict` of collection properties

        :returns: `bool` of add result
        """

        type_ = meta.get('type', 'feature')

        if type_ == 'feature':
            provider_name = API_BACKEND_TYPE
        elif type_ == 'record':
            provider_name = f'{API_BACKEND_TYPE}Catalogue'

        collection = {
            'type': 'collection',
            'title': {
                'en': meta.get('title')
            },
            'description': {
                'en': meta.get('description')
            },
            'keywords': {
                'en': meta.get('keywords')
            },
            'extents': {
                'spatial': {
                    'bbox': meta.get('bbox'),
                    'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
                }
            },
            'providers': [{
                'type': type_,
                'name': provider_name,
                'data': f"http://{API_BACKEND_HOST}:{API_BACKEND_PORT}/{meta.get('id')}.*",  # noqa
                'id_field': meta.get('id_field'),
                'time_field': meta.get('time_field'),
                'title_field': meta.get('title_field')
            }]
        }

        if meta['links']:
            collection['links'] = []
            for link in meta['links']:
                collection['links'].append({
                    'type': 'text/html',
                    'rel': 'canonical',
                    'title': 'information',
                    'href': link
                })

        with API_CONFIG.open() as fh:
            yaml_config = yaml_load(fh)

        yaml_config['resources'][meta.get('id')] = collection

        with API_CONFIG.open("w") as fh:
            yaml_dump(fh, yaml_config)

        return True

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection

        :param name: name of collection

        :returns: `bool` of delete collection result
        """

        with API_CONFIG.open() as fh:
            yaml_config = yaml_load(fh)

        yaml_config['resources'].pop(name)

        with API_CONFIG.open("w") as fh:
            yaml_dump(fh, yaml_config)

        return True

    def __repr__(self):
        return f'<BaseConfig> ({self.config})'
