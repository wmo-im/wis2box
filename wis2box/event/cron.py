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
import time

import click

from wis2box import cli_helpers
from wis2box.api import setup_collection
from wis2box.event.messages import gcm
# from wis2box.handler import Handler

LOGGER = logging.getLogger(__name__)


@click.command()
@click.pass_context
@cli_helpers.OPTION_PATH
@click.option('--interval', '-i', help='Polling interval', default=5)
@cli_helpers.OPTION_VERBOSITY
def cron(ctx, path, interval, verbosity):
    """Subscribe to a broker/topic"""
    click.echo('Adding messages collection')
    setup_collection(meta=gcm())

    LOGGER.info(f"Listening to {path} every {interval} second")
    # TODO: CRON Workflow to replace  wis2box.cron
    # TODO: Data clean capacity
    # TODO: Data archive capacity
    # TODO: Handler workflow?
    while True:
        time.sleep(interval)
