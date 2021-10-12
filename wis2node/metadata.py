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
from typing import Union

from pygeometa.core import read_mcf
from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema
from pygeometa.schemas.wmo_wigos import WMOWIGOSOutputSchema

from wis2node import cli_helpers
from wis2node.catalogue import delete_metadata, upsert_metadata
from wis2node.env import DATADIR
from wis2node.oscar import get_station_report, upload_station_metadata

LOGGER = logging.getLogger(__name__)


@click.group()
def metadata():
    """Metadata management"""
    pass


@click.group()
def discovery():
    """Discovery metadata management"""
    pass


@click.group()
def station():
    """Station metadata management"""
    pass


def gen_metadata(mcf: dict, schema: str) -> Union[dict, str]:
    """
    Generate metadata in a given schema

    :param mcf: `dict` of MCF file
    :param schema: `str` of metadata schema to generate

    :returns: `dict` or `str` of metadata representation
    """

    if schema == 'oarec-record':
        pygeometa_schema_obj = OGCAPIRecordOutputSchema
    elif schema == 'wmo-wigos':
        pygeometa_schema_obj = WMOWIGOSOutputSchema
    else:
        msg = f'Unsupported metadata schema {schema}'
        LOGGER.error(msg)
        raise ValueError(msg)

    LOGGER.debug(f'Generating metadata in schema {schema}')
    return pygeometa_schema_obj().write(mcf)


def parse_record(metadata_record: bytes) -> dict:
    """
    Parses metadata into OARec record

    :param metadata_record: string of metadata

    :return: `dict` of OARec record metadata
    """

    LOGGER.debug('reading MCF')
    return read_mcf(metadata_record)


@click.command()
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
@cli_helpers.ARGUMENT_FILEPATH
def sync(ctx, filepath, verbosity):
    """Syncs local station metadata in with WMO OSCAR/Surface"""

    for line in filepath:
        wsi = line.strip()
        try:
            station_report = get_station_report(wsi)
        except RuntimeError:
            click.echo('Station not found')

        filename = f'{DATADIR}/metadata/station/{wsi}.json'
        LOGGER.debug(f'Writing file to {filename}')
        with open(filename, 'w') as fh:
            json.dump(station_report, fh)


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    try:
        record = parse_record(filepath.read())
        if 'facility' in record:
            station_metadata = gen_metadata(record, 'wmo-wigos')
            upload_station_metadata(station_metadata)
        else:
            upsert_metadata(gen_metadata(record, 'oarec-record'))
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('identifier')
def unpublish(ctx, identifier):
    """Deletes a discovery metadata record from the catalogue"""

    delete_metadata(identifier)


station.add_command(publish)
station.add_command(sync)
discovery.add_command(publish)
discovery.add_command(unpublish)

metadata.add_command(station)
metadata.add_command(discovery)
