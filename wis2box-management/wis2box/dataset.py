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

import click

from wis2box import cli_helpers
from wis2box.data import add_collection
from wis2box.data_mappings import get_data_mappings
from wis2box.metadata.discovery import publish, unpublish

LOGGER = logging.getLogger(__name__)

class Dataset:
    def __init__(self, path: Union[Path, str]) -> None:
        self.path = str(path)
        self.dotpath = None
        self.dirpath = None

        self.metadata_id = None
        self.topic_hierarchy = None

        # determine if path matches a metadata_id
        for metadata_id, data_mappings in get_data_mappings().items():
            if metadata_id in self.path:
                self.metadata_id = metadata_id
                self.topic_hierarchy = data_mappings['topic_hierarchy']

        if self.metadata_id is None:
            # otherwise directory represents topic_hierarchy
            if not self.path.startswith('origin/a/wis2'):
                self.topic_hierarchy = f'origin/a/wis2/{self.path}'
            else:
                self.topic_hierarchy = self.path
            for metadata_id, data_mappings in get_data_mappings().items():
                if self.topic_hierarchy == data_mappings['topic_hierarchy']:
                    self.metadata_id = metadata_id

        if '/' in self.path:
            LOGGER.debug('Transforming from directory to dotted path')
            self.dirpath = self.path
            self.dotpath = self.path.replace('/', '.')
        elif '.' in self.path:
            LOGGER.debug('Transforming from dotted to directory path')
            self.dotpath = self.path
            self.dirpath = self.path.replace('.', '/')


@click.group()
def dataset():
    """Dataset workflow"""
    pass

@click.command('publish')
@click.pass_context
@cli_helpers.ARGUMENT_FILEPATH
@cli_helpers.OPTION_VERBOSITY
def publish_(ctx, filepath, verbosity):
    """Publishes a dataset"""

    ctx.invoke(publish, filepath=filepath, verbosity=verbosity)
    filepath.seek(0)
    ctx.invoke(add_collection, filepath=filepath, verbosity=verbosity)


@click.command('unpublish')
@click.pass_context
@click.argument('identifier')
@click.option('--force', '-f', default=False, is_flag=True,
              help='Force delete associated data from API')
@cli_helpers.OPTION_VERBOSITY
def unpublish_(ctx, identifier, verbosity, force=False):
    """Unpublishes a dataset"""

    ctx.invoke(unpublish, identifier=identifier, verbosity=verbosity,
               force=force)


dataset.add_command(publish_)
dataset.add_command(unpublish_)
