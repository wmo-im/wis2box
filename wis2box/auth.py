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
import logging
import requests
from secrets import token_hex

from wis2box import cli_helpers
from wis2box.topic_hierarchy import validate_and_load
from wis2box.env import AUTH_URL

LOGGER = logging.getLogger(__name__)


def is_resource_open(topic: str) -> bool:
    """
    Checks if topic has access control configured

    :param topic: `str` topic hierarchy

    :returns: `bool` of result
    """

    th, _ = validate_and_load(topic)
    headers = {'X-Original-URI': th.dotpath}
    r = requests.get(f'{AUTH_URL}/authorize', headers=headers)
    return r.ok


def is_token_authorized(auth_key: str, topic: str) -> bool:
    """
    Checks if token is authorized to access a topic

    :param auth_key: `str` auth_key
    :param topic: `str` topic hierarchy

    :returns: `bool` of result
    """
    headers = {
        'X-Original-URI': topic,
        'Authorization': f'Bearer {auth_key}',
    }
    r = requests.get(f'{AUTH_URL}/authorize', headers=headers)
    return r.ok


@click.group()
def auth():
    """Auth workflow"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
def is_restricted(ctx, topic_hierarchy):
    """Check if topic has access control"""
    click.echo(not is_resource_open(topic_hierarchy))


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.argument('token')
def has_access(ctx, topic_hierarchy, token):
    """Check if a token has access to a topic"""
    click.echo(is_token_authorized(token, topic_hierarchy))


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.option(
    '--yes', '-y', default=False, is_flag=True, help='Automatic yes to prompts'
)
@click.argument('token', required=False)
def add_token(ctx, topic_hierarchy, yes, token):
    """Add access token for a topic"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    if token is None:
        click.echo('Generating random token')
        token = token_hex(32)

    if yes:
        click.echo(f'Using token: {token}')
    elif not click.confirm(f'Continue with token: {token}', prompt_suffix='?'):
        return

    data = {'topic': topic_hierarchy, 'token': token}

    r = requests.post(f'{AUTH_URL}/add_token', data=data)
    click.echo(r.json().get('description'))
    return r.ok


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.argument('token', required=False, nargs=-1)
def remove_token(ctx, topic_hierarchy, token):
    """Delete one to many tokens for a topic"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    data = {'topic': topic_hierarchy}

    if token:
        # Delete all tokens for a given th
        data['token'] = token

    r = requests.post(f'{AUTH_URL}/remove_token', data=data)
    click.echo(r.json().get('description'))
    return r.ok


auth.add_command(add_token)
auth.add_command(has_access)
auth.add_command(is_restricted)
auth.add_command(remove_token)
