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

import click
import json
import logging

import yaml

from csv2bufr import transform as transform_csv2bufr

from wis2node import cli_helpers
from wis2node.env import DATADIR_PUBLIC
from wis2node.data.base import AbstractData

LOGGER = logging.getLogger(__name__)


class ObservationData(AbstractData):
    """Observation data"""
    def __init__(self, input_data: str, mappings: dict,
                 discovery_metadata: dict, station_metadata: dict = {}):
        """
        Abstract data initializer

        :param input_data: `str` of data payload
        :param discovery_metadata: `dict` of discovery metadata MCF
        :param station_metadata: `dict` of station metadata
        """

        super().__init__(input_data, discovery_metadata)

        self.file_extension = 'bufr4'
        self.mappings = mappings
        self.station_metadata = station_metadata

        self.data_category = discovery_metadata['wis2node']['data_category']
        self.country_code = discovery_metadata['wis2node']['country_code']
        self.originating_centre = discovery_metadata['wis2node']['originating_centre']  # noqa
        self.station_type = discovery_metadata['wis2node']['station_type']

    def transform(self) -> bool:
        LOGGER.debug('Processing data')
        self.output_data = transform_csv2bufr(self.input_data, self.mappings,
                                              self.station_metadata)
        return True

    @property
    def public_filepath(self):
        return (DATADIR_PUBLIC /
                self.date /
                'wis' /
                self.data_category /
                self.country_code /
                self.originating_centre /
                self.station_type)


def process_data(data: str, mappings: dict, discovery_metadata: dict,
                 station_metadata: dict) -> bool:

    d = ObservationData(data, mappings, discovery_metadata, station_metadata)
    d.transform()
    d.publish()


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_DISCOVERY_METADATA
@cli_helpers.OPTION_STATION_METADATA
@cli_helpers.OPTION_MAPPINGS
@cli_helpers.OPTION_VERBOSITY
def process(ctx, filepath, discovery_metadata, station_metadata, mappings,
            verbosity):
    """Process observations"""

    click.echo(f'Processing {filepath}')

    try:
        _ = process_data(filepath.read(), json.load(mappings),
                         yaml.load(discovery_metadata, Loader=yaml.SafeLoader),
                         json.load(station_metadata))
    except Exception as err:
        raise click.ClickException(err)

    click.echo("Done")


@click.group()
def observations():
    """Observation data manageement"""
    pass


observations.add_command(process)
