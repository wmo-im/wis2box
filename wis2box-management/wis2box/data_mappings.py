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
import os
from pathlib import Path

from wis2box.util import yaml_load

LOGGER = logging.getLogger(__name__)

DATADIR = os.environ.get('WIS2BOX_DATADIR')
DATA_MAPPINGS = Path(DATADIR) / 'data-mappings.yml'

if not DATA_MAPPINGS.exists():
    msg = f'Please create a data mappings file in {DATADIR}'
    LOGGER.error(msg)
    raise RuntimeError(msg)

try:
    with DATA_MAPPINGS.open() as fh:
        DATADIR_DATA_MAPPINGS = yaml_load(fh)
        assert DATADIR_DATA_MAPPINGS is not None
except Exception as err:
    DATADIR_DATA_MAPPINGS = None
    msg = f'Missing data mappings: {err}'
    LOGGER.error(msg)
    raise EnvironmentError(msg)
