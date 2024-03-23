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

from owslib.ogcapi.records import Records

from wis2box.env import (DOCKER_BROKER, DOCKER_API_URL)
from wis2box.plugin import load_plugin, PLUGINS

LOGGER = logging.getLogger(__name__)


def refresh_data_mappings():
    # load plugin for local broker and publish refresh request
    defs_local = {
        'codepath': PLUGINS['pubsub']['mqtt']['plugin'],
        'url': DOCKER_BROKER,
        'client_type': 'dataset-manager'
    }
    local_broker = load_plugin('pubsub', defs_local)
    success = local_broker.pub('wis2box/data_mappings/refresh', '{}', qos=0)
    if not success:
        LOGGER.error('Failed to refresh data mappings')


def get_data_mappings() -> dict:
    """
    Get data mappings

    :returns: `dict` of data mappings definitions
    """

    data_mappings = {}

    oar = Records(DOCKER_API_URL)

    try:
        records = oar.collection_items('discovery-metadata')
        for record in records['features']:
            # skip records without data mappings
            if 'wis2box' not in record:
                continue
            if 'topic_hierarchy' not in record['wis2box']:
                continue
            if 'data_mappings' not in record['wis2box']:
                continue
            key = record['wis2box']['topic_hierarchy']
            value = record['wis2box']['data_mappings']
            value['metadata_id'] = record['id']
            data_mappings[key] = value
    except Exception as err:
        msg = f'Issue loading data mappings: {err}'
        LOGGER.error(msg)
        raise EnvironmentError(msg)

    return data_mappings
