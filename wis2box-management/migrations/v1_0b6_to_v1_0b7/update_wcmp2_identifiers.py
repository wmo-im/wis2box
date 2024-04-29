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

import argparse
import json
import os
from pathlib import Path

from elasticsearch import Elasticsearch

from wis2box.env import (API_BACKEND_URL, DATADIR, STORAGE_PUBLIC,
                         STORAGE_SOURCE)
from wis2box.log import LOGGER, setup_logger
from wis2box.storage import put_data, delete_data
from wis2box.util import json_serial, yaml_load

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG').upper()
setup_logger(loglevel=LOG_LEVEL)

es_index = 'discovery-metadata'
maxrecords = 1000

data_mappings_file = Path(DATADIR) / 'data-mappings.yml'

try:
    with data_mappings_file.open() as fh:
        DATA_MAPPINGS = yaml_load(fh)
except FileNotFoundError as err:
    LOGGER.error(f'Data mappings file not found at {data_mappings_file}')
    raise err


def migrate(dryrun):
    LOGGER.info('Updating discovery data in Elasticsearch index')
    LOGGER.info('Connecting to API ...')
    try:
        es = Elasticsearch(API_BACKEND_URL)
    except Exception as err:
        LOGGER.error(f'Error connecting to {API_BACKEND_URL}')
        raise err

    try:
        res = es.search(index=es_index,
                        query={'match_all': {}},
                        size=maxrecords)
    except Exception as err:
        LOGGER.error(f'Error fetching data from {es_index}')
        raise err

    nhits = res['hits']['hits']
    LOGGER.info(f'Processing {nhits} records')

    for hit in nhits:
        record = hit['_source']
        old_record_id = record['id']
        record['id'] = old_record_id.replace('x-wmo', 'wmo')
        LOGGER.info(f"Updating discovery metadata record {record['id']}")

        th = record['wis2box']['topic_hierarchy']

        if th not in DATA_MAPPINGS['data'].keys():
            LOGGER.info('No matching topic found')
        else:
            record['wis2box']['data_mappings'] = DATA_MAPPINGS['data'][th]
            record_str = json.dumps(record, default=json_serial, indent=4)

            if dryrun:
                LOGGER.info('dryrun == True, writing updates to stdout')
                LOGGER.info(f'Updated record: {record_str}')
            else:
                LOGGER.info('Updating index ...')
                try:
                    es.delete(index=es_index, id=old_record_id)
                    es.index(index=es_index, id=record['id'], document=record)
                    storage_path = f"{STORAGE_SOURCE}/{STORAGE_PUBLIC}/metadata/{old_record_id}.json" # noqa
                    delete_data(storage_path)
                    data_bytes = record_str.encode('utf-8')
                    put_data(data_bytes, storage_path, 'application/geo+json')
                except Exception as err:
                    LOGGER.error('Error applying update')
                    raise err


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dryrun',
                        action='store_true',
                        help='Run in dry run mode (output to stdout)')
    args = parser.parse_args()
    # Execute
    LOGGER.info('Running wis2box migration from v1_0b6 to v1_0b7 (update wcmp2 identifiers)')  # noqa
    migrate(dryrun=args.dryrun)
