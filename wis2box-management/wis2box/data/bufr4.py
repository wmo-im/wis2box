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
import tempfile
from typing import Union

from bufr2geojson import BUFRParser
from eccodes import (
    codes_bufr_copy_data,
    codes_bufr_new_from_samples,
    codes_bufr_new_from_file,
    codes_get_message,
    codes_clone,
    codes_set,
    codes_set_array,
    codes_release,
    codes_get,
    codes_get_array
)

from wis2box.data.base import BaseAbstractData
from wis2box.metadata.station import get_geometry, get_valid_wsi

LOGGER = logging.getLogger(__name__)
TEMPLATE = codes_bufr_new_from_samples("BUFR4")
TIME_PATTERNS = ['%Y', '%m', '%d', '%H', '%M', '%S']
TIME_NAMES = [
    'typicalYear',
    'typicalMonth',
    'typicalDay',
    'typicalHour',
    'typicalMinute',
    'typicalSecond'
]

HEADERS = ["edition", "masterTableNumber", "bufrHeaderCentre",
           "bufrHeaderSubCentre", "updateSequenceNumber", "dataCategory",
           "internationalDataSubCategory", "dataSubCategory",
           "masterTablesVersionNumber", "localTablesVersionNumber",
           "typicalYear", "typicalMonth", "typicalDay", "typicalHour",
           "typicalMinute", "typicalSecond",
           "numberOfSubsets", "observedData", "compressedData"]


class ObservationDataBUFR(BaseAbstractData):
    """Observation data"""

    def transform(
        self, input_data: Union[Path, bytes], filename: str = ''
    ) -> bool:

        LOGGER.debug('Procesing BUFR data')
        input_bytes = self.as_bytes(input_data)

        # FIXME: figure out how to pass a bytestring to ecCodes BUFR reader
        tmp = tempfile.NamedTemporaryFile()
        with open(tmp.name, 'wb') as f:
            f.write(input_bytes)

        # workflow
        # check for multiple messages
        # split messages and process
        data = {}
        with open(tmp.name, 'rb') as fh:
            while data is not None:
                data = codes_bufr_new_from_file(fh)
                if data is not None:
                    self.transform_message(data)
                    codes_release(data)

    def transform_message(self, bufr_in: int) -> None:
        """
        Parse single BUFR message
        :param bufr_in: `int` of ecCodes pointer to BUFR message
        :returns: `None`
        """
        # workflow
        # check for multiple subsets
        # add necessary components for WSI in BUFR
        # split subsets into individual messages and process
        try:
            codes_set(bufr_in, 'unpack', True)
        except Exception as err:
            LOGGER.error(f'Error unpacking message: {err}')
            raise err

        # get descriptors present in the file
        descriptors = codes_get_array(bufr_in, "expandedDescriptors").tolist()

        # prepare the headers for the new messages
        headers = {}
        for header in HEADERS:
            headers[header] = codes_get(bufr_in, header)
        # original to be split by subset, so set the number of subsets to 1
        headers['numberOfSubsets'] = 1
        # set the master table version number
        table_version = max(
            28, codes_get(bufr_in, 'masterTablesVersionNumber')
        )
        headers['masterTablesVersionNumber'] = table_version
        # set the unexpanded descriptors
        out_ue = codes_get_array(bufr_in, 'unexpandedDescriptors').tolist()
        if 301150 not in out_ue:
            out_ue.insert(0, 301150)
        headers['unexpandedDescriptors'] = out_ue

        # loop over the subsets, create a new message for each
        num_subsets = codes_get(bufr_in, 'numberOfSubsets')
        LOGGER.debug(f'Found {num_subsets} subsets')
        for i in range(num_subsets):
            idx = i + 1
            LOGGER.debug(f'Processing subset {idx}')
            LOGGER.debug('Extracting subset')
            codes_set(bufr_in, 'extractSubset', idx)
            codes_set(bufr_in, 'doExtractSubsets', 1)
            # copy the replication factors
            if 31000 in descriptors:
                try:
                    short_replication_factors = codes_get_array(bufr_in, "shortDelayedDescriptorReplicationFactor").tolist()  # noqa
                except Exception as e:
                    short_replication_factors = []
                    LOGGER.error(e.__class__.__name__)
            if 31001 in descriptors:
                try:
                    replication_factors = codes_get_array(bufr_in, "delayedDescriptorReplicationFactor").tolist()  # noqa
                except Exception as e:
                    replication_factors = []
                    LOGGER.error(e.__class__.__name__)
            if 31002 in descriptors:
                try:
                    extended_replication_factors = codes_get_array(bufr_in, "extendedDelayedDescriptorReplicationFactor").tolist()  # noqa
                except Exception as e:
                    extended_replication_factors = []
                    LOGGER.error(e.__class__.__name__)
            LOGGER.debug('Copying template BUFR')
            subset_out = codes_clone(TEMPLATE)

            # set the replication factors, this needs to be done before
            # setting the unexpanded descriptors
            if (31000 in descriptors) and (len(short_replication_factors) > 0):  # noqa
                codes_set_array(subset_out, "inputShortDelayedDescriptorReplicationFactor", short_replication_factors)  # noqa
            if (31001 in descriptors) and (len(replication_factors) > 0):
                codes_set_array(subset_out, "inputDelayedDescriptorReplicationFactor", replication_factors)  # noqa
            if (31002 in descriptors) and (len(extended_replication_factors) > 0):  # noqa
                codes_set_array(subset_out, "inputExtendedDelayedDescriptorReplicationFactor", extended_replication_factors)  # noqa

            # we need to copy all the headers, not just the
            # unexpandedDescriptors and MT number

            for k, v in headers.items():
                if isinstance(v, list):
                    codes_set_array(subset_out, k, v)
                else:
                    codes_set(subset_out, k, v)

            LOGGER.debug('Cloning subset to new message')
            subset = codes_clone(bufr_in)
            self.transform_subset(subset, subset_out)
            codes_release(subset)
            codes_release(subset_out)

    def transform_subset(self, subset: int, subset_out: int) -> None:
        """
        Parse single BUFR message subset
        :param subset: `int` of ecCodes pointer to input BUFR
        :param subset_out: `int` of ecCodes pointer to output BUFR
        :returns: `None`
        """
        # workflow
        # - check for WSI,
        #   - if None, lookup using tsi
        # - check for location,
        #   - if None, use geometry from station report
        # - check for time,
        #   - if temporal extent, use end time
        #   - set times in header
        # - write a separate BUFR
        parser = BUFRParser(raise_on_error=True)
        LOGGER.debug('Parsing subset')
        try:
            parser.as_geojson(subset, id='')
        except Exception as err:
            LOGGER.warning(err)

        try:
            temp_wsi = parser.get_wsi()
            temp_tsi = parser.get_tsi()
        except Exception as err:
            LOGGER.warning(err)

        try:
            location = parser.get_location()
            if location is None or None in location['coordinates']:
                raise Exception("Missing location in BUFR")
        except Exception:
            LOGGER.error(f"Error parsing location from subset with wsi={temp_wsi}, use coordinates from station metadata") # noqa

        try:
            data_date = parser.get_time()
        except Exception:
            LOGGER.error(f"Error parsing time from subset with wsi={temp_wsi}, skip this subset") # noqa
            self.publish_failure_message(
                        description="Invalid date in BUFR data",
                        wsi=temp_wsi)
            return

        del parser

        LOGGER.debug(f'Processing temp_wsi: {temp_wsi}, temp_tsi: {temp_tsi}')
        wsi = get_valid_wsi(wsi=temp_wsi, tsi=temp_tsi)
        if wsi is None:
            msg = 'Station not in station list: '
            msg += f'wsi={temp_wsi} tsi={temp_tsi}; skipping'
            LOGGER.error(msg)
            self.publish_failure_message(
                        description="Station not in station list",
                        wsi=temp_wsi)
            return

        try:
            LOGGER.debug('Copying wsi to BUFR')
            [series, issuer, number, tsi] = wsi.split('-')
            codes_set(subset_out, '#1#wigosIdentifierSeries', int(series))
            codes_set(subset_out, '#1#wigosIssuerOfIdentifier', int(issuer))
            codes_set(subset_out, '#1#wigosIssueNumber', int(number))
            codes_set(subset_out, '#1#wigosLocalIdentifierCharacter', tsi)
            codes_bufr_copy_data(subset, subset_out)

            if location is None or None in location['coordinates']:
                msg = 'Missing coordinates in BUFR, setting from station report'  # noqa
                LOGGER.warning(msg)
                location = get_geometry(wsi)
                LOGGER.debug(f'New coordinates: {location}')
                long, lat, elev = location.get('coordinates')
                codes_set(subset_out, '#1#longitude', long)
                codes_set(subset_out, '#1#latitude', lat)
                codes_set(subset_out, '#1#heightOfStationGroundAboveMeanSeaLevel', elev)  # noqa

            if '/' in data_date:
                data_date = data_date.split('/')[1]

            isodate = datetime.strptime(data_date, '%Y-%m-%dT%H:%M:%SZ')

            for (name, p) in zip(TIME_NAMES, TIME_PATTERNS):
                codes_set(subset_out, name, int(isodate.strftime(p)))

            isodate_str = isodate.strftime('%Y%m%dT%H%M%S')

            rmk = f"WIGOS_{wsi}_{isodate_str}"
            LOGGER.info(f'Publishing with identifier: {rmk}')

            LOGGER.debug('Writing bufr4')
            bufr4 = codes_get_message(subset_out)
            self.output_data[rmk] = {
                'bufr4': bufr4,
                '_meta': {
                    'identifier': rmk,
                    'wigos_station_identifier': wsi,
                    'data_date': isodate,
                    'geometry': location,
                    'relative_filepath': self.get_local_filepath(isodate)
                }
            }
            LOGGER.debug('Finished processing subset')
        except Exception as err:
            LOGGER.error(f'Failed processing subset: {err}')
            self.publish_failure_message(
                        description='Failed processing subset',
                        wsi=wsi)

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
