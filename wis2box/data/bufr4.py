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
from io import BytesIO
import logging
from pathlib import Path
import tempfile
from typing import Union

from bufr2geojson import BUFRParser
from eccodes import (
    codes_bufr_copy_data,
    codes_bufr_new_from_samples,
    codes_bufr_new_from_file,
    codes_clone,
    codes_set,
    codes_set_array,
    codes_release,
    codes_get,
    codes_get_array,
    codes_write,
)

from wis2box.data.base import BaseAbstractData
from wis2box.metadata.station import get_geometry, get_valid_wsi

LOGGER = logging.getLogger(__name__)


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
        # - check for WSI,
        #   - if None, lookup using tsi
        # - check for location,
        #   - if None, use geometry from station report
        # - check for time,
        #   - if temporal extent, use end time
        #   - set times in header
        # - write a separate BUFR

        with open(tmp.name, 'rb') as fh:
            bufr_in = codes_bufr_new_from_file(fh)

            try:
                codes_set(bufr_in, 'unpack', True)
            except Exception as err:
                LOGGER.error(f'Error unpacking message: {err}')
                raise err

            num_subsets = codes_get(bufr_in, 'numberOfSubsets')
            LOGGER.debug(f'Found {num_subsets} subsets')

            table_version = max(
                28, codes_get(bufr_in, 'masterTablesVersionNumber')
            )
            inUE = codes_get_array(bufr_in, 'unexpandedDescriptors')
            outUE = inUE.tolist()
            if 301150 not in outUE:
                outUE.insert(0, 301150)

            for i in range(num_subsets):
                idx = i + 1
                LOGGER.debug(f'Processing subset {idx}')

                codes_set(bufr_in, 'extractSubset', idx)
                codes_set(bufr_in, 'doExtractSubsets', 1)

                LOGGER.debug('Cloning subset to new message')
                subset = codes_clone(bufr_in)

                try:
                    LOGGER.debug('Unpacking')
                    codes_set(subset, 'unpack', True)
                except Exception as err:
                    LOGGER.error(f'Error unpacking message: {err}')
                    raise err

                try:
                    LOGGER.debug('Parsing subset')
                    parser = BUFRParser()
                    parser.as_geojson(subset, id='')
                except Exception as err:
                    LOGGER.warning(err)

                temp_wsi = parser.get_wsi()
                tsi = temp_wsi.split('-')[-1]
                LOGGER.debug(f'Processing wsi: {temp_wsi}, tsi: {tsi}')

                wsi = get_valid_wsi(wsi=temp_wsi, tsi=tsi)
                if wsi is None:
                    msg = f'Failed to publish, wsi: {temp_wsi}, tsi: {tsi}'
                    LOGGER.error(msg)
                    continue

                LOGGER.debug('Creating template BUFR')
                template = codes_bufr_new_from_samples("BUFR4")
                codes_set(template, 'masterTablesVersionNumber', table_version) # noqa
                codes_set_array(template, 'unexpandedDescriptors', outUE)

                LOGGER.debug('Copying wsi to BUFR')
                [series, issuer, number, tsi] = wsi.split('-')
                codes_set(template, '#1#wigosIdentifierSeries', int(series)) # noqa
                codes_set(template, '#1#wigosIssuerOfIdentifier', int(issuer)) # noqa
                codes_set(template, '#1#wigosIssueNumber', int(number)) # noqa
                codes_set(template, '#1#wigosLocalIdentifierCharacter', tsi) # noqa
                codes_bufr_copy_data(subset, template)
                codes_release(subset)

                try:
                    location = parser.get_location()
                except Exception as err:
                    LOGGER.warning(err)

                if None in location['coordinates']:
                    LOGGER.debug('Setting coordinates from station report')
                    location = get_geometry(wsi)
                    long, lat, elev = location.get('coordinates')
                    codes_set(template, '#1#longitude', long)
                    codes_set(template, '#1#latitude', lat)
                    codes_set(template, '#1#heightOfStationGroundAboveMeanSeaLevel', elev) # noqa

                try:
                    data_date = parser.get_time()
                except Exception as err:
                    LOGGER.info(err)

                try:
                    if '/' in data_date:
                        data_date = data_date.split('/')
                        data_date = data_date[1]
                    isodate = datetime.strptime(
                        data_date, '%Y-%m-%dT%H:%M:%SZ'
                    )
                except Exception as err:
                    LOGGER.warning(f'Invalid time: {data_date} {err}')
                    LOGGER.error(f'Failed to publish: {wsi}')
                    continue

                field_names = [
                    'typicalYear',
                    'typicalMonth',
                    'typicalDay',
                    'typicalHour',
                    'typicalMinute',
                    'typicalSecond'
                ]
                patterns = ['%Y', '%m', '%d', '%H', '%M', '%S']
                for (name, p) in zip(field_names, patterns):
                    codes_set(template, name, int(isodate.strftime(p)))
                isodate = isodate.strftime('%Y%m%dT%H%M%S')

                rmk = f"WIGOS_{wsi}_{isodate}"
                LOGGER.info(f'Publishing with identifier: {rmk}')

                LOGGER.debug('Writing bufr4')
                with BytesIO() as file_handle:
                    codes_set(template, "pack", True)
                    codes_write(template, file_handle)
                    codes_release(template)
                    file_handle.seek(0)
                    bufr4 = file_handle.read()

                del parser
                yield {
                    'bufr4': bufr4,
                    '_meta': {
                        'identifier': rmk,
                        'wigos_station_identifier': wsi,
                        'data_date': data_date,
                        'geometry': location
                    }
                }

            codes_release(bufr_in)

    def get_local_filepath(self, date_):
        yyyymmdd = date_[0:10]  # date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
