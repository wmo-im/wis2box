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
from typing import Union

from pygeometa.core import read_mcf

LOGGER = logging.getLogger(__name__)


class BaseMetadata:
    """base metadata"""

    def __init__(self):
        pass

    def generate(self, mcf: dict, schema: str = None) -> Union[dict, str]:
        """
        Generate metadata in a given schema

        :param mcf: `dict` of MCF file
        :param schema: `str` of metadata schema to generate

        :returns: `dict` or `str` of metadata representation
        """

        raise NotImplementedError()

    def parse_record(self, metadata_record: bytes) -> dict:
        """
        Parses MCF metadata into dict

        :param metadata_record: string of metadata

        :return: `dict` of MCF
        """

        LOGGER.debug('reading MCF')
        return read_mcf(metadata_record)
