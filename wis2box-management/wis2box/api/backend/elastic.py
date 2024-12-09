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
from typing import Tuple

from wis2box.api.backend.base import BaseBackend
from wis2box.util import datetime_days_ago

logging.getLogger('elasticsearch').setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

# default index settings
SETTINGS = {
    'number_of_shards': 1,
    'number_of_replicas': 0
}

MAPPINGS = {
    'properties': {
        'geometry': {
            'type': 'geo_shape'
        },
        'time': {
            'properties': {
                'interval': {
                    'type': 'date',
                    'null_value': '1850',
                    'format': 'year||year_month||year_month_day||date_time||t_time||t_time_no_millis',  # noqa
                    'ignore_malformed': True
                }
            }
        },
        'reportId': {
            'type': 'text',
            'fields': {
                'raw': {
                    'type': 'keyword'
                }
            }
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
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'wigos_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
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

MAPPINGS_OBS = {
    'properties': {
        'geometry': {
            'type': 'geo_shape'
        },
        'properties': {
            'properties': {
                'name': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'reportTime': {
                    'type': 'date',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'reportId': {
                    'type': 'text',
                    'fields': {
                        'raw': {
                            'type': 'keyword'
                        }
                    }
                },
                'phenomenonTime': {
                    'type': 'text'
                },
                'wigos_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'units': {
                    'type': 'text'
                },
                'value': {
                    'type': 'float',
                    'coerce': True
                },
                'description': {
                    'type': 'text'
                },
            }
        }
    }
}

MAPPINGS_STATIONS = {
    'properties': {
        'geometry': {
            'type': 'geo_shape'
        },
        'properties': {
            'properties': {
                'name': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'wigos_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'traditional_station_identifier': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'barometer_height': {
                    'type': 'float'
                },
                'facility_type': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'territory_name': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'wmo_region': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'url': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
                    }
                },
                'topics': {
                    'type': 'text',
                    'fields': {
                        'raw': {'type': 'keyword'}
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

        self.conn = Elasticsearch(self.url, timeout=30,
                                  max_retries=10, retry_on_timeout=True)

    @staticmethod
    def es_id(collection_id: str) -> Tuple[str]:
        """
        Make collection_id ES friendly

        :param collection_id: `str` name of collection

        :returns: `str` of ES index
        """
        return collection_id.lower().replace(':', '-')

    def list_collections(self) -> list:
        """
        List collections

        :returns: `list` of collection names
        """

        return [index for index in self.conn.indices.get_alias(index="*")]

    def add_collection(self, collection_id: str) -> dict:
        """
        Add a collection

        :param collection_id: `str` name of collection

        :returns: `bool` of result
        """

        if collection_id == 'stations':
            mappings = MAPPINGS_STATIONS
        elif collection_id in ['discovery-metadata', 'messages']:
            mappings = MAPPINGS
        else:
            mappings = MAPPINGS_OBS

        es_index = self.es_id(collection_id)

        if self.has_collection(collection_id):
            msg = f'index {es_index} exists'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        LOGGER.debug('Creating index')
        self.conn.options().indices.create(index=es_index, mappings=mappings,
                                           settings=SETTINGS)

        return self.has_collection(collection_id)

    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection

        :param collection_id: name of collection

        :returns: `bool` of delete result
        """
        es_index = self.es_id(collection_id)

        if not self.has_collection(collection_id):
            msg = f'index {es_index} does not exist'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        if self.conn.indices.exists(index=es_index):
            self.conn.indices.delete(index=es_index)

        return not self.has_collection(collection_id)

    def reindex_collection(self, collection_id_source: str, collection_id_target: str) -> bool: # noqa
        """
        Reindex a collection

        :param collection_id_source: name of source collection
        :param collection_id_target: name of target collection

        :returns: `bool` of reindex result
        """
        es_index_source = self.es_id(collection_id_source)
        es_index_target = self.es_id(collection_id_target)

        print(f'Copying {es_index_source} to {es_index_target}')
        try:
            helpers.reindex(self.conn, es_index_source, es_index_target)
        except helpers.BulkIndexError as e:
            LOGGER.error('Bulk indexing failed for some documents:')
            for err in e.errors:
                LOGGER.error(err)

        return self.has_collection(collection_id_target)

    def has_collection(self, collection_id: str) -> bool:
        """
        Checks a collection

        :param collection_id: name of collection

        :returns: `bool` of collection result
        """
        es_index = self.es_id(collection_id)
        indices = self.conn.indices

        return indices.exists(index=es_index)

    def upsert_collection_items(self, collection_id: str, items: list) -> str:
        """
        Add or update collection items

        :param collection_id: name of collection
        :param items: list of GeoJSON item data `dict`'s

        :returns: `str` identifier of added item
        """
        es_index = self.es_id(collection_id)

        if not self.has_collection(collection_id):
            LOGGER.debug(f'Index {es_index} does not exist.  Creating')
            self.add_collection(es_index)

        def gendata(features):
            """
            Generator function to yield features
            """

            for feature in features:
                LOGGER.debug(f'Feature: {feature}')
                feature['properties']['id'] = feature['id']

                yield {
                    '_index': es_index,
                    '_id': feature['id'],
                    '_source': feature
                }
        success, errors = helpers.bulk(self.conn, gendata(items), raise_on_error=False) # noqa
        if errors:
            for error in errors:
                LOGGER.error(f"Indexing error: {error}")
            raise RuntimeError(f"Upsert failed with {len(errors)} errors")

    def delete_collection_item(self, collection_id: str, item_id: str) -> str:
        """
        Delete an item from a collection

        :param collection_id: name of collection
        :param item_id: `str` of item identifier

        :returns: `bool` of delete result
        """

        LOGGER.debug(f'Deleting {item_id} from {collection_id}')
        try:
            _ = self.conn.delete(index=collection_id, id=item_id)
        except Exception as err:
            msg = f'Item deletion failed: {err}'
            raise RuntimeError(msg)

        return True

    def delete_collections_by_retention(self, days: int) -> bool:
        """
        Delete collections by retention date

        :param days: `int` of number of days

        :returns: `None`
        """

        indices = self.conn.indices.get(index='*').keys()

        before = datetime_days_ago(days)
        # also delete future data
        after = datetime_days_ago(-1)

        msg_query_by_date = {
            'query': {
                'bool': {
                    'should': [
                        {'range': {'properties.pubTime': {'lte': before}}},
                        {'range': {'properties.pubTime': {'gte': after}}}
                    ]
                }
            }
        }
        obs_query_by_date = {
            'query': {
                'bool': {
                    'should': [
                        {'range': {'properties.reportTime': {'lte': before}}},
                        {'range': {'properties.reportTime': {'gte': after}}}
                    ]
                }
            }
        }

        for index in indices:
            if index == 'messages':
                query_by_date = msg_query_by_date
            elif index.startswith('urn-wmo-md'):
                query_by_date = obs_query_by_date
            else:
                # don't run delete-query on other indexes
                LOGGER.info(f'items for index={index} will not be deleted')
                continue
            LOGGER.info(f'deleting documents from index={index} older than {days} days ({before}) or newer than {after}')  # noqa
            result = self.conn.delete_by_query(index=index, **query_by_date)
            LOGGER.info(f'deleted {result["deleted"]} documents from index={index}')  # noqa

        return

    def flush(self, collection: str):
        """
        Flush a given index to ensure persistence

        :param collection: name of collection

        :returns: `None`
        """

        self.conn.indices.flush(index=self.es_id(collection))

    def __repr__(self):
        return f'<ElasticBackend> (url={self.url})'
