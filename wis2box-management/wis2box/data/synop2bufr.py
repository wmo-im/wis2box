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
from pathlib import Path
from typing import Union

from wis2box.data.base import BaseAbstractData
from wis2box.api import execute_process

LOGGER = logging.getLogger(__name__)


class ObservationDataSYNOP2BUFR(BaseAbstractData):
    """Synoptic observation data"""
    def __init__(self, defs: dict) -> None:
        """
        ObservationDataSYNOP2BUFR data initializer

        :param def: `dict` object of resource mappings

        :returns: `None`
        """

        super().__init__(defs)

        self.mappings = {}

    def publish(self) -> bool:
        """
        Publish data

        :returns: `bool` of result
        """

        LOGGER.debug('skip publish for call_synop_publish-plugin')
        return True

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Processing SYNOP ASCII data')

        if isinstance(input_data, Path):
            LOGGER.debug('input_data is a Path')
            filename = input_data.name

        file_match = self.validate_filename_pattern(filename)

        if file_match is None:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)

        input_bytes = self.as_bytes(input_data)
        LOGGER.debug('extracting year and month from filename')
        try:
            year = int(file_match.group(1))
            month = int(file_match.group(2))
        except IndexError:
            msg = 'Missing year and/or month in filename pattern'
            LOGGER.error(msg)
            raise ValueError(msg)

        process_name = 'wis2box-synop2bufr'
        # execute process
        inputs = {
            "data": input_bytes.decode(),
            "year": year,
            "month": month,
            "channel": self.topic_hierarchy.dirpath,
            "notify": self.enable_notification
        }
        result = execute_process(process_name, inputs)
        if 'errors' in result:
            for error in result['errors']:
                LOGGER.error(f'{process_name} error: {error}')
        return True
