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
from copy import deepcopy
import json
import logging

from pygeometa.helpers import json_serial
from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema

from wis2node import cli_helpers
from wis2node.env import API_URL
from wis2node.catalogue import delete_metadata, upsert_metadata
from wis2node.metadata.base import BaseMetadata

LOGGER = logging.getLogger(__name__)


class DiscoveryMetadata(BaseMetadata):
    def __init__(self):
        super().__init__()

    def generate(self, mcf: dict) -> str:
        """
        Generate OARec discovery metadata

        :param mcf: `dict` of MCF file

        :returns: `str` of metadata representation
        """

        md = deepcopy(mcf)

        identifier = md['metadata']['identifier']

        LOGGER.debug('Adding distribution links')
        oafeat_link = {
            'url': f"{API_URL}/collections/{identifier}",
            'type': 'OAFeat',
            'name': identifier,
            'description': identifier,
            'function': 'collection'
        }
        md['distribution'] = {'oafeat': oafeat_link}

        LOGGER.debug('Generating OARec discovery metadata')
        record = OGCAPIRecordOutputSchema().write(md, stringify=False)

        anytext_bag = [
            md['identification']['title']['en'],
            md['identification']['abstract']['en']
        ]

        for k, v in md['identification']['keywords'].items():
            anytext_bag.extend(v['keywords']['en'])

        record['properties']['_metadata-anytext'] = ' '.join(anytext_bag)

        LOGGER.debug('Adding canonical link')
        canonical_link = {
            'url': f"{API_URL}/collections/discovery-metadata/{identifier}",
            'type': 'OARec',
            'name': identifier,
            'description': identifier,
            'function': 'canonical'
        }
        record['links'].append(canonical_link)

        return json.dumps(record, default=json_serial, indent=4)


@click.group()
def discovery():
    """Discovery metadata management"""
    pass


@click.command()
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish(ctx, filepath, verbosity):
    """Inserts or updates discovery metadata to catalogue"""

    click.echo(f'Publishing discovery metadata from {filepath.name}')
    try:
        dm = DiscoveryMetadata()
        record = dm.parse_record(filepath.read())
        upsert_metadata(dm.generate(record))
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Done')


@click.command()
@click.pass_context
@click.argument('identifier')
@cli_helpers.OPTION_VERBOSITY
def unpublish(ctx, identifier, verbosity):
    """Deletes a discovery metadata record from the catalogue"""

    click.echo('Unpublishing discovery metadata {identifier}')
    delete_metadata(identifier)


discovery.add_command(publish)
discovery.add_command(unpublish)
