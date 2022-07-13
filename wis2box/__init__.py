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

__version__ = '0.2.0'

import click

from wis2box.data import data
from wis2box.env import environment
from wis2box.metadata import metadata
from wis2box.pubsub import pubsub
from wis2box.api import api
from wis2box.auth import auth


@click.group()
@click.version_option(version=__version__)
def cli():
    """WIS 2.0 in a box"""
    pass


cli.add_command(environment)
cli.add_command(data)
cli.add_command(metadata)
cli.add_command(api)
cli.add_command(auth)
cli.add_command(pubsub)
