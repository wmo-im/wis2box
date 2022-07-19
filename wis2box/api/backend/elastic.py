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

from copy import deepcopy
import logging

from elasticsearch import Elasticsearch, helpers
from parse import parse
from isodate import parse_date

from wis2box.api.backend.base import BaseBackend
from wis2box.util import older_than

LOGGER = logging.getLogger(__name__)

# default index settings
SETTINGS = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'properties': {
            'geometry': {
                'type': 'geo_shape'
            },
            'properties': {
                'properties': {
                    'resultTime': {
                        'type': 'date',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'pubTime': {
                        'type': 'date',
                        'fields': {
                            'raw': {
                                'type': 'keyword'
                            }
                        }
                    },
                    'phenomenonTime': {
                        'type': 'text'
                    },
                    'value': {
                        'type': 'float',
                        'coerce': True
                    },
                    'metadata': {
                        'properties': {
                            'value': {
                                'type': 'float',
                                'coerce': True
                            }
                        }
                    }
                }
            }
        }
    }
}


class ElasticBackend(BaseBackend):
    """Elasticsearch API backend"""

    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters (RFC 1738 URL)
        """

        super().__init__(defs)

        self.type = 'Elasticsearch'
        self.url = defs.get('url').rstrip('/')

        self.conn = Elasticsearch([self.url], timeout=30,
                                  max_retries=10, retry_on_timeout=True)

    @staticmethod
    def es_id(collection_id: str) -> str:
        """
        Make collection_id ES friendly

        :param collection_id: `str` name of collection

        :returns: `str` ES index name
        """
        return collection_id.lower()

    def add_collection(self, collection_id: str) -> dict:
        """
        Add a collection

        :param collection_id: `str` name of collection

        :returns: `dict` API provider configuration
        """

        es_index = self.es_id(collection_id)
        es_template = f'{es_index}.'

        if self.conn.indices.exists(es_index):
            msg = f'index {es_index} exists'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        if self.conn.indices.exists_template(es_template):
            msg = f'template {es_template} exists'
            LOGGER.warning(msg)
            # raise RuntimeError(msg)

        settings = deepcopy(SETTINGS)

        if self._is_dataset(es_index):
            LOGGER.debug('dataset index detected')
            LOGGER.debug('creating index template')
            settings['index_patterns'] = [f'{es_template}*']
            settings['order'] = 0
            settings['version'] = 1
            self.conn.indices.put_template(es_template, settings)

        else:
            LOGGER.debug('metadata index detected')
            self.conn.indices.create(index=es_index, body=settings)

        return {
            'type': 'feature',
            'name': 'Elasticsearch',
            'data': f'{self.url}/{es_index}.*',
            'id_field': 'id',
            'time_field': 'resultTime'
        }

    def delete_collection(self, collection_id: str) -> None:
        """
        Delete a collection

        :param collection_id: name of collection

        :returns: `None`
        """

        es_index = self.es_id(collection_id)
        es_template = f'{es_index}.'

        if not self.conn.indices.exists(es_index):
            msg = f'index {es_index} does not exist'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        self.conn.indices.delete(index=es_index)

        if self.conn.indices.exists_template(es_template):
            self.conn.indices.delete_template(es_template)

    def upsert_collection_items(self, collection_id: str, items: list) -> str:
        """
        Add or update collection items

        :param collection_id: name of collection
        :param items: list of GeoJSON item data `dict`'s

        :returns: `str` identifier of added item
        """

        es_index = self.es_id(collection_id)

        if (not self._is_dataset(es_index) and
                not self.conn.indices.exists(es_index)):
            LOGGER.debug('Index {es_index} does not exist.  Creating')
            self.add_collection(es_index)

        def gendata(features):
            """
            Generator function to yield features
            """

            for feature in features:
                LOGGER.debug(f'Feature: {feature}')
                es_index2 = es_index
                feature['properties']['id'] = feature['id']
                if self._is_dataset(collection_id):
                    LOGGER.debug('Determinining index date from OM GeoJSON')
                    try:
                        date_ = parse_date(feature['properties']['resultTime'])
                    except KeyError:
                        date_ = parse_date(feature['properties']['pubTime'])
                    es_index2 = f"{es_index}.{date_.strftime('%Y-%m-%d')}"
                yield {
                    '_index': es_index2,
                    '_id': feature['id'],
                    '_source': feature
                }

        helpers.bulk(self.conn, gendata(items))

    def delete_collection_item(self, collection_id: str, item_id: str) -> str:
        """
        Delete an item from a collection

        :param collection_id: name of collection
        :param item_id: `str` of item identifier

        :returns: `str` identifier of added item
        """

        raise NotImplementedError()

    def delete_collections_by_retention(self, days: int) -> bool:
        """
        Delete collections by retention date

        :param days: `int` of number of days

        :returns: `None`
        """

        indices = self.conn.indices.get('*').keys()

        pattern = '{index_name}.{Y:d}-{M:d}-{d:d}'

        for index in indices:
            match = parse(pattern, index)
            if match:
                idx = f"{match.named['Y']}-{match.named['M']}-{match.named['d']}"  # noqa
                if older_than(idx, days):
                    LOGGER.debug(f'Index {index} older than {days} days')
                    LOGGER.debug('Deleting')
                    self.delete_collection(index)

        return

    def _is_dataset(self, collection_id) -> bool:
        """
        Check whether the index is a dataset (and thus
        needs daily index management)

        :param collection_id: name of collection

        :returns: `bool` of evaluation
        """

        if '.' in collection_id or collection_id == 'messages':
            return True
        else:
            return False

    def __repr__(self):
        return f'<ElasticBackend> (url={self.url})'
