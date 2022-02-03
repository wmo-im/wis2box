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

from elasticsearch import Elasticsearch, helpers

from wis2node.api.backend.base import BaseBackend

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
            }
        }
    }
}


class ElasticBackend(BaseBackend):
    """Elasticsearch API backend"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
                     (host, port, username, password)
        """

        super().__init__(defs)

        self.type = 'Elasticsearch'

        url_settings = f'{self.host}:{self.port}'

        LOGGER.debug(f'URL settings: {url_settings}')

        if None in [self.username, self.password]:
            self.conn = Elasticsearch([url_settings])
        else:
            LOGGER.debug(f'Connecting using username {self.username}')
            self.conn = Elasticsearch(
                [url_settings], http_auth=(self.username, self.password))

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
        if self.conn.indices.exists(es_index):
            msg = f'index {es_index} exists'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        self.conn.indices.create(index=es_index, body=SETTINGS)

        scheme = 'https' if self.port == 443 else 'http'
        return {
            'type': 'feature',
            'name': 'Elasticsearch',
            'data': f'{scheme}://{self.host}:{self.port}/{es_index}',
            'id_field': 'id'
        }

    def delete_collection(self, collection_id: str) -> None:
        """
        Delete a collection

        :param collection_id: name of collection

        :returns: `None`
        """

        es_index = self.es_id(collection_id)
        if not self.conn.indices.exists(es_index):
            msg = f'index {es_index} does not exist'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        self.conn.indices.delete(index=es_index)

    def upsert_collection_items(self, collection_id: str, items: list) -> str:
        """
        Add or update a collection item

        :param collection_id: name of collection
        :param items: list of GeoJSON item data `dict`'s

        :returns: `str` identifier of added item
        """

        es_index = self.es_id(collection_id)

        def gendata(features):
            """
            Generator function to yield features
            """

            for feature in features:
                feature["properties"]["id"] = feature["id"]
                yield {
                    "_index": es_index,
                    "_id": feature['id'],
                    "_source": feature
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

    def __repr__(self):
        return f'<BaseBackend> (host={self.host}, port={self.port})'
