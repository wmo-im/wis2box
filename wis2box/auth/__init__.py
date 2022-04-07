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
from secrets import choice
from string import ascii_letters, digits

from wis2box import cli_helpers
from wis2box.topic_hierarchy import validate_and_load
from wis2box.auth.base import BaseAuth
from wis2box.env import AUTH_STORE

LOGGER = logging.getLogger(__name__)


def is_resource_open(topic: str) -> bool:
    """
    Checks if topic has access control configured

    :param topic: `str` topic hierarchy

    :returns: `bool` of result
    """
    auth_db = BaseAuth(AUTH_STORE)
    th, _ = validate_and_load(topic)
    return auth_db.is_resource_open(th.dotpath)


def is_token_authorized(auth_key: str, topic: str) -> bool:
    """
    Checks if token is authorized to access a topic

    :param auth_key: `str` auth_key
    :param topic: `str` topic hierarchy

    :returns: `bool` of result
    """
    auth_db = BaseAuth(AUTH_STORE)
    th, _ = validate_and_load(topic)
    return auth_db.is_token_authorized(auth_key, th.dotpath)


@click.group()
def auth():
    """Auth workflow"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
def is_restricted(ctx, topic_hierarchy):
    """Check if topic has access control"""
    click.echo(is_resource_open(topic_hierarchy))


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.argument('token')
def has_access(ctx, topic_hierarchy, token):
    """Check if a token has access to a topic"""
    click.echo(is_token_authorized(token, topic_hierarchy))


@click.command()
@click.pass_context
def show(ctx):
    """Show topics with access control configured"""
    auth_db = BaseAuth(AUTH_STORE)
    [click.echo(f'Topic: {topic}') for topic in auth_db.topics()]


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.argument('token', required=False)
def add_token(ctx, topic_hierarchy, token):
    """Add access token for a topic"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    if token is None:
        click.echo(f'Generating token for {topic_hierarchy}')
        token = ''.join(choice(ascii_letters + digits) for _ in range(24))

    if not click.confirm(f'Continue with token: {token}', prompt_suffix='?'):
        return

    auth_db = BaseAuth(AUTH_STORE)
    auth_db.add(token, topic_hierarchy)


@click.command()
@click.pass_context
@cli_helpers.OPTION_TOPIC_HIERARCHY
@click.argument('token', required=False, nargs=-1)
def remove_tokens(ctx, topic_hierarchy, token):
    """Delete one to many tokens for a topic"""

    if topic_hierarchy is None:
        raise click.ClickException('Missing -th/--topic-hierarchy')

    auth_db = BaseAuth(AUTH_STORE)

    if not token:
        # Delete all tokens for a given th
        return auth_db.delete_by_topic_hierarchy(topic_hierarchy)
    else:
        # Delete specific tokens
        return [auth_db.delete_by_token(t, topic_hierarchy) for t in token]


auth.add_command(is_restricted)
auth.add_command(has_access)
auth.add_command(show)
auth.add_command(add_token)
auth.add_command(remove_tokens)
