###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# 'License'); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################
import argparse
import os
import re
import time

from wis2box.api.backend import load_backend
from wis2box.env import (STORAGE_SOURCE, STORAGE_PUBLIC)
from wis2box.log import LOGGER, setup_logger
from wis2box.storage import list_content, get_data, put_data
from wis2box.util import older_than

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
setup_logger(loglevel=LOG_LEVEL)


def update_datasets(days: int = 5):
    LOGGER.info('Recreating backend collections')
    api_backend = load_backend()
    backend_collections = api_backend.list_collections()
    for collection in backend_collections:
        # skip collection not staring with urn
        if not collection.startswith('urn'):
            continue
        if api_backend.has_collection(collection):
            print(f'Recreating {collection}')
            api_backend.delete_collection(collection)
            api_backend.add_collection(collection)
    # re-upload BUFR4 data for days_to_backfill
    LOGGER.info(f'Backfilling {days} days')
    storage_path_public = f'{STORAGE_SOURCE}/{STORAGE_PUBLIC}'
    for obj in list_content(storage_path_public):
        # check if obj['basedir'] is formatted like YYYY-MM-DD
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', obj['basedir']):
            continue
        # check if filename is .bufr4
        if not obj['filename'].endswith('.bufr4'):
            continue
        # check if older than days
        if older_than(obj['basedir'], days):
            continue
        else:
            # re-upload data
            storage_path = obj['fullpath']
            print(f'Re-process {storage_path}')
            put_data(data=get_data(storage_path), path=storage_path)
            # sleep 1. second to allow for the data to be processed
            time.sleep(1)


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--days-to-backfill',
                        action='store',
                        help='Number of days to backfill',
                        type=int,
                        default=5)
    args = parser.parse_args()
    # Execute
    LOGGER.info('Running wis2box migration from 1.0b8 to 1.0.0rc1 (update data collections)')  # noqa
    update_datasets(days=args.days_to_backfill)
