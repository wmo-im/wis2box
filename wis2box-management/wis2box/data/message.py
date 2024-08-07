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
from datetime import datetime
from typing import Union

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class MessageData(BaseAbstractData):
    """
    DataPublish:

    transform sets output_data to input_data
    using metadata received by the plugin
    """

    def __init__(self, defs: dict) -> None:
        try:
            self._meta = defs['_meta']
        except KeyError:
            error = f'No _meta in defs: {defs}'
            LOGGER.error(error)
            raise KeyError(error)
        super().__init__(defs)

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:
        """
        Transform input_data to output_data

        :param input_data: input data
        :param filename: filename of input data
        :param _meta: metadata of input data

        :returns: `bool` of result
        """

        suffix = filename.split('.')[-1]
        rmk = filename.split('.')[0]
        input_bytes = self.as_bytes(input_data)

        # convert isoformat to datetime
        self._meta['data_date'] = datetime.fromisoformat(self._meta['data_date']) # noqa
        # add relative filepath to _meta
        self._meta['relative_filepath'] = self.get_local_filepath(self._meta['data_date']) # noqa

        self.output_data[rmk] = {
            suffix: input_bytes,
            '_meta': self._meta
        }
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.metadata_id
