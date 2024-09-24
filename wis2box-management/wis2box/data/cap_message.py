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

from datetime import datetime
import logging
from pathlib import Path
from typing import Union

from capvalidator import validate_cap_message, get_dates

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class CAPMessageData(BaseAbstractData):
    """
    DataPublish:

    transform sets output_data to input_data
    using metadata received by the plugin
    """

    def __init__(self, defs: dict) -> None:
        """
        CAPMessageData data initializer

        :param def: `dict` object of resource mappings

        :returns: `None`
        """

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

        [rmk, suffix] = filename.rsplit('.', 1)
        input_bytes = self.as_bytes(input_data)

        # get the sent date from the CAP XML
        sent_date = get_dates(input_bytes).sent
        # convert isoformat to datetime
        _meta = {}
        _meta['data_date'] = datetime.fromisoformat(sent_date)
        # add relative filepath to _meta
        _meta['relative_filepath'] = self.get_local_filepath(_meta['data_date'])  # noqa

        # validate the CAP XML string content using the capvalidator package
        result = validate_cap_message(input_bytes, strict=False)
        if not result.passed:
            LOGGER.error(
                f'Invalid CAP XML, not publishing. Reason: {result.message}')
            return False

        LOGGER.info(
            f'CAP XML is valid, publishing to wis2box. {result.message}')

        self.output_data[rmk] = {
            suffix: input_bytes,
            '_meta': _meta
        }
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.metadata_id
