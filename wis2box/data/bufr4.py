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
import json
from io import BytesIO
import logging
from pathlib import Path
import tempfile
from typing import Union

from bufr2geojson import BUFRParser, transform as as_geojson
from eccodes import (
    codes_bufr_new_from_file,
    codes_clone,
    codes_set,
    codes_release,
    codes_get,
    codes_write
)

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class ObservationDataBUFR2GeoJSON(BaseAbstractData):
    """Observation data"""

    def transform(
        self, input_data: Union[Path, bytes], filename: str = ''
    ) -> bool:

        LOGGER.debug('Procesing BUFR data')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Generating GeoJSON features')
        results = as_geojson(input_bytes, serialize=False)

        LOGGER.debug('Processing GeoJSON features')
        for collection in results:
            # results is an iterator, for each iteration we have:
            # - dict['id']
            # - dict['id']['_meta']
            # - dict['id']
            for id, item in collection.items():
                LOGGER.debug(f'Processing feature: {id}')

                LOGGER.debug('Parsing feature datetime')
                data_date = item['_meta']['data_date']
                if '/' in data_date:
                    # date is range/period, split and get end date/time
                    data_date = data_date.split('/')[1]

                LOGGER.debug('Parsing feature fields')
                items_to_remove = [
                    key for key in item if key not in ('geojson', '_meta')
                ]
                for key in items_to_remove:
                    LOGGER.debug(f'Removing unexpected key: {key}')
                    item.pop(key)

                LOGGER.debug('Populating output data for publication')
                self.output_data[id] = item
                self.output_data[id]['geojson'] = json.dumps(
                    self.output_data[id]['geojson'], indent=4
                )
                self.output_data[id]['_meta'][
                    'relative_filepath'
                ] = self.get_local_filepath(data_date)

        LOGGER.debug('Successfully finished transforming BUFR data')
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath


class ObservationDataBUFR(BaseAbstractData):
    """Oservation data"""

    def transform(
        self, input_data: Union[Path, bytes], filename: str = ''
    ) -> bool:

        LOGGER.debug('Procesing BUFR data')
        input_bytes = self.as_bytes(input_data)

        results = self.check_bufr_data(input_bytes)

        # convert to list
        LOGGER.debug('Iterating over BUFR messages')
        for item in results:
            LOGGER.debug('Parsing feature datetime')
            identifier = item['_meta']['identifier']
            data_date = item['_meta']['data_date']

            self.output_data[identifier] = item
            self.output_data[identifier]['_meta'][
                'relative_filepath'
            ] = self.get_local_filepath(data_date)

        return True

    def check_bufr_data(self, data: bytes) -> dict:

        # FIXME: figure out how to pass a bytestring to ecCodes BUFR reader
        tmp = tempfile.NamedTemporaryFile()
        with open(tmp.name, 'wb') as f:
            f.write(data)

        # workflow
        # check for multiple subsets
        # split subsets into individual messages and process
        # foreach subset:
        # - check for WSI
        # - if None, set from filename regex
        # - check location/time (TODO: how?)
        # - write a separate BUFR
        # - send to as_geojson

        with open(tmp.name, 'rb') as fh:
            bufr_in = codes_bufr_new_from_file(fh)

            try:
                codes_set(bufr_in, 'unpack', True)
            except Exception as err:
                LOGGER.error(f'Error unpacking message: {err}')
                raise err

            num_subsets = codes_get(bufr_in, 'numberOfSubsets')
            LOGGER.debug(f'Found {num_subsets} subsets')

            for i in range(num_subsets):
                idx = i + 1
                LOGGER.debug(f'Processing subset {idx}')

                codes_set(bufr_in, 'extractSubset', idx)
                codes_set(bufr_in, 'doExtractSubsets', 1)

                LOGGER.debug('Cloning subset to new message')
                subset = codes_clone(bufr_in)

                LOGGER.debug('Unpacking')
                try:
                    codes_set(subset, 'unpack', True)
                except Exception as err:
                    LOGGER.error(f'Error unpacking message: {err}')
                    raise err

                LOGGER.debug('Parsing as geoJSON')
                parser = BUFRParser()
                parser.as_geojson(subset, id='')

                wsi = parser.get_wsi()
                # TODO: Validate wsi from BUFR parser.

                LOGGER.info('Writing bufr4')
                file_handle = BytesIO()
                codes_write(subset, file_handle)
                codes_release(subset)
                file_handle.seek(0)
                bufr4 = file_handle.read()

                data_date = parser.get_time()
                if "/" in data_date:
                    data_date = data_date.split("/")
                    data_date = data_date[1]

                isodate = datetime.strptime(
                    data_date, '%Y-%m-%dT%H:%M:%SZ'
                ).strftime('%Y%m%dT%H%M%S')
                rmk = f"WIGOS_{wsi}_{isodate}"
                LOGGER.info(f'Publishing with identifier: {rmk}')

                item = {
                    'bufr4': bufr4,
                    '_meta': {
                        'identifier': rmk,
                        'wigos_id': wsi,
                        'data_date': parser.get_time(),
                        'geometry': parser.get_location()
                    }
                }
                yield item

    # def set_wigos_id(self, filename):
    #     table_version = max(
    #         28, codes_get(bufr_in, 'masterTablesVersionNumber')
    #     )
    #     LOGGER.debug(f'Using masterTablesVersionNumber: {table_version}')

    #     inUE = codes_get_array(bufr_in, 'unexpandedDescriptors')
    #     outUE = inUE.tolist()
    #     if 301150 not in outUE:
    #         LOGGER.debug('Adding WIGOS sequence to unexpandedDescriptors')
    #         outUE.insert(0, 301150)

    #     LOGGER.debug('Preparing BUFR4 template')
    #     codes_set(bufr_out, 'numberOfSubsets', num_subsets)
    #     codes_set(
    #         bufr_out,
    #         'masterTablesVersionNumber',
    #         table_version,
    #     )
    #     codes_set_array(bufr_out, 'unexpandedDescriptors', outUE)

    #             # TODO: '#1#wigosIssueNumber' or f'#{idx}#wigosIssueNumber'
    #     # TODO: Attempt to get wsi from filename
    #     wsi_series = \
    #         codes_get(subset, '#1#wigosIdentifierSeries')
    #     wsi_issuer = \
    #         codes_get(subset, '#1#wigosIssuerOfIdentifier')
    #     wsi_number = \
    #         codes_get(subset, '#1#wigosIssueNumber')
    #     wsi_local = \
    #         codes_get(subset, '#1#wigosLocalIdentifierCharacter')
    #     wigosId = f'{wsi_series}-{wsi_issuer}-{wsi_number}-{wsi_local}'
    #     LOGGER.debug(f'WIGOS Identifier Series: {wsi_series}')
    #     LOGGER.debug(f'WIGOS Issuer of Identifier: {wsi_issuer}')
    #     LOGGER.debug(f'WIGOS Issue Number: {wsi_number}')
    #     LOGGER.debug(f'WIGOS Local Identifier Character: {wsi_local}')

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
