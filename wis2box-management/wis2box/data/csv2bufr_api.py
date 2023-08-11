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


class ObservationDataCSV2BUFR(BaseAbstractData):
    """Synoptic observation data"""
    def __init__(self, defs: dict) -> None:
        """
        ObservationDataCSV2BUFR data initializer

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

        LOGGER.debug('Processing CSV data')

        if isinstance(input_data, Path):
            LOGGER.debug('input_data is a Path')
            filename = input_data.name

        file_match = self.validate_filename_pattern(filename)

        if file_match is None:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)
        
        input_bytes = self.as_bytes(input_data)

        process_name = 'wis2box-csv-process'
        # execute process
        inputs = {
            "data": input_bytes.decode(),
            "mapping": self.mappings['bufr4'],
            "channel": self.topic_hierarchy,
            "notify": self.enable_notification
        }
        result = execute_process(process_name, inputs)
        for error in result['errors']:
            LOGGER.error(f'{process_name} error: {error}')
        return True
