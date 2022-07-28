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
import requests

from wis2box.api.config.base import BaseConfig
from wis2box.env import API_BACKEND_TYPE, API_BACKEND_URL, API_CONFIG, DOCKER_API_URL
from wis2box.util import yaml_dump, yaml_load

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
        self.url = f'{DOCKER_API_URL}/admin/resources'

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
        resource_id = meta.get('id')

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
                'data': f"{API_BACKEND_URL}/{resource_id}",  # noqa
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

        if self.has_collection(resource_id):
            r = requests.put(f'{self.url}/{resource_id}', json=collection)
        else:
            content = {resource_id: collection}
            r = requests.post(self.url, json=content)

        r.raise_for_status()
        return True

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection

        :param name: name of collection

        :returns: `bool` of delete collection result
        """

        r = requests.delete(f'{self.url}/{name}')
        return r.status_code == requests.codes.ok

    def has_collection(self, name: str) -> dict:
        """
        Checks a collection

        :param name: name of collection

        :returns: `dict` of collection result
        """
        r = requests.get(f'{self.url}/{name}')
        return r.status_code == requests.codes.ok

    def __repr__(self):
        return f'<PygeoapiConfig> ({self.config})'
