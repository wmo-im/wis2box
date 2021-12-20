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

        url_settings = {
            'host': self.host,
            'port': self.port
        }

        if self.port == 443:
            url_settings['scheme'] = 'https'

        LOGGER.debug('URL settings: {}'.format(url_settings))

        if None in [self.username, self.password]:
            self.conn = Elasticsearch([url_settings])
        else:
            LOGGER.debug(f'Connecting using username {self.username}')
            self.conn = Elasticsearch(
                [url_settings], http_auth=(self.username, self.password))

    def add_collection(self, collection_id: str) -> None:
        """
        Add a collection

        :param collection_id: name of collection

        :returns: `None`
        """

        if self.conn.indices.exists(collection_id):
            msg = f'index {collection_id} exists'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        self.conn.indices.create(index=collection_id, body=SETTINGS)

    def delete_collection(self, collection_id: str) -> None:
        """
        Delete a collection

        :param collection_id: name of collection

        :returns: `None`
        """

        if not self.conn.indices.exists(collection_id):
            msg = f'index {collection_id} does not exist'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        self.conn.indices.delete(index=collection_id)

        raise NotImplementedError()

    def upsert_collection_items(self, collection_id: str, items: list) -> str:
        """
        Add or update a collection item

        :param collection_id: name of collection
        :param items: list of GeoJSON item data `dict`'s

        :returns: `str` identifier of added item
        """

        def gendata(features):
            """
            Generator function to yield features
            """

            for feature in features:
                yield {
                    "_index": collection_id,
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
