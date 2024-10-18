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

from typing import Any, Tuple

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
            value = record['wis2box']['data_mappings']
            if 'wmo:topicHierarchy' not in record['properties']:
                LOGGER.error(f'No topic hierarchy for {record["id"]}')
                continue
            value['topic_hierarchy'] = record['properties']['wmo:topicHierarchy'] # noqa
            metadata_id = record['id']
            data_mappings[metadata_id] = value
    except Exception as err:
        msg = f'Issue loading data mappings: {err}'
        LOGGER.error(msg)
        raise EnvironmentError(msg)

    return data_mappings


def validate_and_load(path: str,
                      data_mappings: dict = None,
                      gts_mappings: dict = None,
                      file_type: str = None
                      ) -> Tuple[str, Tuple[Any]]:
    """
    Validate path and load plugins

    :param path: `str` of path
    :param data_mappings: `dict` of data mappings
    :param file_type: `str` the type of file we are processing, e.g. csv, bufr, xml  # noqa
    :param fuzzy: `bool` of whether to do fuzzy matching of path
                  (e.g. "*foo.bar.baz*).
                  Defaults to `False` (i.e. "foo.bar.baz")

    :returns: tuple of metadata_id and list of plugins objects
    """

    LOGGER.debug(f'Validating path: {path}')
    LOGGER.debug(f'Data mappings {data_mappings}')

    metadata_id = None
    topic_hierarchy = None
    # determine if path matches a metadata_id
    for key in data_mappings.keys():
        if key in path:
            metadata_id = key
            topic_hierarchy = data_mappings[key]['topic_hierarchy']
    # else try to match topic_hierarchy
    if metadata_id is None:
        for key, value in data_mappings.items():
            if (value['topic_hierarchy']).replace('origin/a/wis2/', '') in path:  # noqa
                metadata_id = key
                topic_hierarchy = value['topic_hierarchy']
                break
    if metadata_id is None:
        options = [key for key in data_mappings.keys()] # noqa
        options += [v['topic_hierarchy'].replace('origin/a/wis2/', '') for v in data_mappings.values()]  # noqa
        msg = f'Could not match {path} to dataset, path should include one of the following: {options}'  # noqa
        raise ValueError(msg)

    if 'plugins' not in data_mappings[metadata_id]:
        msg = f'No plugins defined in data-mappings for metadata_id={metadata_id}' # noqa
        LOGGER.error(msg)
        raise ValueError(msg)
    plugins = data_mappings[metadata_id]['plugins']

    if file_type is None:
        LOGGER.warning('File type missing')
        file_type = next(iter(plugins))
        LOGGER.debug(f'File type set to first type: {file_type}')

    if file_type not in plugins:
        msg = f'Unknown file type ({file_type}) for metadata_id={metadata_id}. Did not match any of the following:'  # noqa
        msg += ', '.join(plugins)
        raise ValueError(msg)

    LOGGER.debug(f'Adding plugin definition for {file_type}')

    def data_defs(plugin):
        notify = plugin.get('notify', False)
        data_defs = {
            'metadata_id': metadata_id,
            'íncoming_filepath': path,
            'topic_hierarchy': topic_hierarchy,
            'codepath': plugin['plugin'],
            'pattern': plugin['file-pattern'],
            'template': plugin.get('template'),
            'buckets': plugin.get('buckets', ()),
            'notify': notify,
            'format': file_type
        }
        if notify and gts_mappings:
            for key in gts_mappings.keys():
                # check if string defined by key is contained in path
                if key in path:
                    data_defs['gts_ttaaii'] = gts_mappings[key]['ttaaii']
                    data_defs['gts_cccc'] = gts_mappings[key]['cccc']
                    break
        return data_defs

    plugins_ = [load_plugin('data', data_defs(p), data_mappings)
                for p in plugins[file_type]]
    return metadata_id, plugins_
