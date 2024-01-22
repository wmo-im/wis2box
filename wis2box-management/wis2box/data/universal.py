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

from dateutil.parser import parse

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class UniversalData(BaseAbstractData):
    """Universal data"""

    def __init__(self, defs: dict) -> None:
        super().__init__(defs)

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        filename = Path(filename)
        LOGGER.debug('Procesing data')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Deriving datetime')
        match = self.validate_filename_pattern(filename.name)

        if match is None:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)
        try:
            date_time = match.group(1)
        except IndexError:
            msg = 'Missing date/time in filename pattern'
            LOGGER.error(msg)
            raise ValueError(msg)

        try:
            date_time = parse(date_time)
        except Exception:
            msg = f'Invalid date/time format: {date_time}'
            LOGGER.error(msg)
            raise ValueError(msg)

        rmk = filename.stem
        suffix = filename.suffix.replace('.', '')

        self.output_data[rmk] = {
            suffix: input_bytes,
            '_meta': {
                'identifier': rmk,
                'relative_filepath': self.get_local_filepath(date_time),
                'data_date': date_time
            }
        }

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
