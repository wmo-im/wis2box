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

from enum import Enum
import importlib
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)

PLUGINS = {
    'api_backend': {
        'Elasticsearch': {
            'plugin': 'wis2box.api.backend.elastic.ElasticBackend'
        }
    },
    'api_config': {
        'pygeoapi': {
            'plugin': 'wis2box.api.config.pygeoapi.PygeoapiConfig'
        }
    },
    'pubsub': {
        'mqtt': {
            'plugin': 'wis2box.pubsub.mqtt.MQTTPubSubClient'
        }
    },
    'storage': {
        'S3': {
            'plugin': 'wis2box.storage.minio.MinIOStorage'
         }
     }
}


class PluginTypes(Enum):
    API_BACKEND = 'api_backend'
    API_CONFIG = 'api_config'
    DATA = 'data'
    PUBSUB = 'pubsub'
    STORAGE = 'storage'


def load_plugin(plugin_type: PluginTypes,
                defs: dict,
                data_mappings: dict = None) -> Any:
    """
    loads plugin by type

    :param plugin_type: type of plugin (`data`)
    :param defs: `def` dict of plugin initializers

    :returns: plugin object
    """

    codepath = defs.get('codepath')
    fmt = defs.get('format')

    if plugin_type in ['api_backend', 'api_config', 'pubsub', 'storage']:
        plugin_mappings = PLUGINS
    elif plugin_type == 'data':
        if data_mappings is None:
            LOGGER.error('data_mappings is None')
            raise ValueError('data_mappings is None')
        else:
            plugin_mappings = {'data': data_mappings}
    else:
        msg = f'Invalid plugin type: {plugin_type}'
        LOGGER.error(msg)
        raise InvalidPluginError(msg)

    # check code path is valid
    if '.' not in codepath:
        msg = f'Invalid plugin codepath: {codepath}'
        LOGGER.exception(msg)
        raise InvalidPluginError(msg)

    valid_plugin = False
    for value in plugin_mappings[plugin_type].values():
        if 'plugins' in value:
            for plugin in value['plugins'].get(fmt, ()):
                if codepath == plugin['plugin']:
                    valid_plugin = True
                    break
        else:
            if codepath == value['plugin']:
                valid_plugin = True
                break

    if not valid_plugin:
        msg = f'Plugin {codepath} not found'
        LOGGER.exception(msg)
        raise InvalidPluginError(msg)

    packagename, classname = codepath.rsplit('.', 1)

    LOGGER.debug(f'Package name: {packagename}')
    LOGGER.debug(f'Class name: {classname}')

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)
    plugin = class_(defs)

    return plugin


class InvalidPluginError(Exception):
    """Invalid plugin"""
    pass
