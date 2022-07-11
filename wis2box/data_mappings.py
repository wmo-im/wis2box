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

import os
import logging

from pathlib import Path

from wis2box.util import yaml_load

LOGGER = logging.getLogger(__name__)

LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL', 'ERROR')
LOGFILE = os.environ.get('WIS2BOX_LOGGING_LOGFILE', 'stdout')

if 'WIS2BOX_DATADIR_DATA_MAPPINGS' in os.environ:
    LOGGER.debug('Overriding WIS2BOX_DATADIR_DATA_MAPPINGS')
    try:
        with open(os.environ.get('WIS2BOX_DATADIR_DATA_MAPPINGS')) as fh:
            DATADIR_DATA_MAPPINGS = yaml_load(fh)
            assert DATADIR_DATA_MAPPINGS is not None
    except Exception as err:
        DATADIR_DATA_MAPPINGS = None
        msg = f'Missing data mappings: {err}'
        LOGGER.error(msg)
        raise EnvironmentError(msg)

with (Path(__file__).parent / 'resources' / 'data-mappings.yml').open() as fh:
    DATADIR_DATA_MAPPINGS = yaml_load(fh)
try:
    DATADIR = Path(os.environ.get('WIS2BOX_DATADIR'))
    DATADIR_INCOMING = DATADIR / 'data' / 'incoming'
    DATADIR_PUBLIC = DATADIR / 'data' / 'public'
    DATADIR_ARCHIVE = DATADIR / 'data' / 'archive'
    DATADIR_CONFIG = DATADIR / 'config'
    API_CONFIG = Path(os.environ.get('WIS2BOX_API_CONFIG'))
except (OSError, TypeError):
    msg = 'Configuration filepaths do not exist!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)