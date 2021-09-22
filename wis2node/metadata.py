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

import json
import logging

from pygeometa.core import read_mcf
from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema

LOGGER = logging.getLogger(__name__)

METADATA_RECORD_TYPES = [
    'mcf',
    'oarec-record'
]


def parse_record(metadata_record: bytes, metadata_type: str) -> dict:
    """
    Parses metadata into OARec record

    :param metadata_record: string of metadata
    :param metadata_type: metadata type

    :return: `dict` of OARec record metadata
    """

    record = None

    if metadata_type == 'mcf':
        LOGGER.debug('reading MCF')
        record = read_mcf(metadata_record)
        return OGCAPIRecordOutputSchema().write(record)

    elif metadata_type == 'oarec-record':
        return json.load(metadata_record)
