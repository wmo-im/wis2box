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

import json
import logging

import click
from tinydb import Query, TinyDB, where

from wis2node import cli_helpers
from wis2node.env import CATALOGUE_BACKEND
from wis2node.metadata import parse_record

LOGGER = logging.getLogger(__name__)


def upsert_metadata(record: str) -> None:
    """
    Upserts record metadata into catalogue

    :param record: `dict` of record metadata

    :returns: None
    """

    rec_dict = json.loads(record)

    LOGGER.info(f'Connecting to catalogue {CATALOGUE_BACKEND}')
    db = TinyDB(CATALOGUE_BACKEND)

    record_query = Query()

    try:
        res = db.upsert(rec_dict, record_query.id == rec_dict['id'])
        LOGGER.info(f"Record {rec_dict['id']} upserted with internal id {res}")
    except Exception as err:
        LOGGER.error(f'record insertion failed: {err}', exc_info=1)
        raise

    return


@click.group()
def catalogue():
    """Catalogue management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_METADATA_TYPE
@cli_helpers.OPTION_VERBOSITY
def upsert(ctx, filepath, metadata_type, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    if metadata_type is None:
        raise click.ClickException('missing --metadata-type/-m option')

    try:
        upsert_metadata(parse_record(filepath.read(), metadata_type))
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


@click.command()
@click.pass_context
def delete(ctx):
    """Deletes a discovery metadata record from the catalogue"""
    pass


catalogue.add_command(delete)
catalogue.add_command(upsert)
