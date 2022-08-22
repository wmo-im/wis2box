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
from requests import Session, codes
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from wis2box.api.config.base import BaseConfig
from wis2box.env import API_BACKEND_TYPE, API_BACKEND_URL, DOCKER_API_URL
from wis2box.util import is_dataset

LOGGER = logging.getLogger(__name__)


class PygeoapiConfig(BaseConfig):
    """Abstract API config"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
        """

        super().__init__(defs)
        self.url = f'{DOCKER_API_URL}/admin/resources'
        self.http = Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            method_whitelist=['GET', 'PUT', 'DELETE']
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount('https://', adapter)
        self.http.mount('http://', adapter)

    def add_collection(self, name: str, collection: dict) -> bool:
        """
        Add a collection

        :param name: `str` of collection name
        :param collection: `dict` of collection properties

        :returns: `bool` of add result
        """
        if self.has_collection(name):
            r = self.http.put(f'{self.url}/{name}', json=collection)
        else:
            content = {name: collection}
            r = self.http.post(self.url, json=content)

        r.raise_for_status()
        return r.status_code == codes.ok

    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection

        :param name: name of collection

        :returns: `bool` of delete collection result
        """

        r = self.http.delete(f'{self.url}/{name}')
        return r.status_code == codes.ok

    def has_collection(self, name: str) -> bool:
        """
        Checks a collection

        :param name: name of collection

        :returns: `bool` of collection result
        """

        r = self.http.get(f'{self.url}/{name}')
        return r.status_code == codes.ok

    def prepare_collection(self, meta: dict) -> bool:
        """
        Add a collection

        :param meta: `dict` of collection properties

        :returns: `dict` of collection configuration
        """

        resource_id = meta.get('id')
        type_ = meta.get('type', 'feature')

        provider_name = API_BACKEND_TYPE

        if type_ == 'record':
            provider_name = f'{provider_name}Catalogue'

        if is_dataset(resource_id):
            resource_id = f'{resource_id}.*'.lower()

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
                'data': f'{API_BACKEND_URL}/{resource_id}',  # noqa
                'id_field': meta.get('id_field'),
                'time_field': meta.get('time_field'),
                'title_field': meta.get('title_field')
            }]
        }

        if meta.get('time_field') is None:
            collection['providers'][0].pop('time_field')

        if meta.get('links') is not None:
            def make(link):
                if isinstance(link, dict):
                    return link
                else:
                    return {
                        'type': 'text/html',
                        'rel': 'canonical',
                        'title': 'information',
                        'href': link
                    }
            collection['links'] = [make(link) for link in meta['links']]

        return collection

    def __repr__(self):
        return '<PygeoapiConfig>'
