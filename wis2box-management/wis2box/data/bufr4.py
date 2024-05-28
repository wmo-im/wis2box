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

import base64
import logging

from datetime import datetime
from pathlib import Path
from typing import Union

from wis2box.api import execute_api_process
from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class ObservationDataBUFR(BaseAbstractData):
    """Observation data"""
    def __init__(self, defs: dict) -> None:
        """
        ObservationDataBUFR data initializer

        :param def: `dict` object of resource mappings

        :returns: `None`
        """

        super().__init__(defs)

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        LOGGER.debug('Processing BUFR4')
        data = self.as_string(input_data, base64_encode=True)

        payload = {
            'inputs': {
                'channel': self.topic_hierarchy.replace('origin/a/wis2/', ''),
                'notify': False,
                'data': data
            }
        }

        process_name = 'wis2box-bufr2bufr'
        result = execute_api_process(process_name, payload)

        try:
            # check for errors
            for error in result['errors']:
                LOGGER.error(error)
            # check for warnings
            for warning in result['warnings']:
                LOGGER.warning(warning)
        except KeyError:
            LOGGER.error(f'KeyError in result={result}')
            return False

        if 'data_items' not in result:
            LOGGER.error(f'file={filename} failed to convert to BUFR4 (result={result})') # noqa
            return False

        # loop over data_items in response
        for data_item in result['data_items']:
            filename = data_item['filename']
            suffix = filename.split('.')[-1]
            rmk = filename.split('.')[0]
            # convert data_item['data'] to bytes
            input_bytes = base64.b64decode(data_item['data'].encode('utf-8'))
            # define _meta
            _meta = data_item['_meta']
            # convert isoformat to datetime
            _meta['data_date'] = datetime.fromisoformat(_meta['data_date'])
            # add relative filepath to _meta
            _meta['relative_filepath'] = self.get_local_filepath(_meta['data_date']) # noqa
            # add to output_data
            self.output_data[rmk] = {
                suffix: input_bytes,
                '_meta': _meta
            }

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.metadata_id
