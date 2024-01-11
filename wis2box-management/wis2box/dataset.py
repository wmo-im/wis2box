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

from wis2box.data import add_collection, delete_collection
from wis2box.metadata.discovery import publish, unpublish

LOGGER = logging.getLogger(__name__)


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
@cli_helpers.OPTION_VERBOSITY
def unpublish_(ctx, identifier, verbosity):
    """Unpublishes a dataset"""

    # TODO
    # ctx.invoke(delete_collection, collection=identifier, verbosity=verbosity)
    # ctx.invoke(unpublish, identifier=identifier, verbosity=verbosity)


dataset.add_command(publish_)
dataset.add_command(unpublish_)
