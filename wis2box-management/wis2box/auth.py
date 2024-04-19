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
from wis2box.env import AUTH_URL

LOGGER = logging.getLogger(__name__)


def create_token(path: str, token: str) -> bool:
    """
    Creates a token with access control

    :param path: `str` path
    :param token: `str` authentication token

    :returns: `bool` of result
    """
    data = {'path': path, 'token': token}

    r = requests.post(f'{AUTH_URL}/add_token', data=data)
    LOGGER.info(r.json().get('description'))

    return r.ok


def delete_token(path: str, token: str = '') -> bool:
    """
    Creates a token with access control

    :param path: `str` path
    :param token: `str` authentication token

    :returns: `bool` of result
    """
    data = {'path': path}

    if token != '':
        # Delete all tokens for a given th
        data['token'] = token

    r = requests.post(f'{AUTH_URL}/remove_token', data=data)
    click.echo(r.json().get('description'))

    return r.ok


def is_resource_open(path: str) -> bool:
    """
    Checks if path has access control configured

    :param path: `str` path

    :returns: `bool` of result
    """
    headers = {'X-Original-URI': path}

    r = requests.get(f'{AUTH_URL}/authorize', headers=headers)

    return r.ok


def is_token_authorized(path: str, token: str) -> bool:
    """
    Checks if token is authorized to access a path

    :param path: `str` path
    :param token: `str` authentication token

    :returns: `bool` of result
    """
    headers = {
        'X-Original-URI': path,
        'Authorization': f'Bearer {token}',
    }
    r = requests.get(f'{AUTH_URL}/authorize', headers=headers)
    return r.ok


@click.group()
def auth():
    """Auth workflow"""
    pass


@click.command()
@click.pass_context
@cli_helpers.OPTION_DATASET
def is_restricted_dataset(ctx, metadata_id):
    """Check if dataset has access control"""
    click.echo(not is_resource_open(metadata_id))


@click.command()
@click.pass_context
@click.option('--path', '-p')
def is_restricted_path(ctx, path):
    """Check if path has access control"""
    click.echo(not is_resource_open(path))


@click.command()
@click.pass_context
@cli_helpers.OPTION_DATASET
@click.argument('token')
def has_access_dataset(ctx, metadata_id, token):
    """Check if a token has access to a dataset"""
    click.echo(is_token_authorized(metadata_id, token))


@click.command()
@click.pass_context
@click.option('--path', '-p')
@click.argument('token')
def has_access_path(ctx, path, token):
    """Check if a token has access to a path"""
    click.echo(is_token_authorized(path, token))


@click.command()
@click.pass_context
@cli_helpers.OPTION_DATASET
@click.option('--path', '-p')
@click.option('--yes', '-y', default=False, is_flag=True, help='Automatic yes')
@click.argument('token', required=False)
def add_token(ctx, metadata_id, path, yes, token):
    """Add access token for a path or dataset"""

    if metadata_id is not None:
        path = metadata_id
    elif path is not None:
        path = path
    else:
        raise click.ClickException('Missing path or metadata_id')

    token = token_hex(32) if token is None else token
    if yes:
        click.echo(f'Using token: {token}')
    elif not click.confirm(f'Continue with token: {token}', prompt_suffix='?'):
        return

    if create_token(path, token):
        click.echo('Token successfully created')


@click.command()
@click.pass_context
@cli_helpers.OPTION_DATASET
@click.option('--path', '-p')
@click.argument('token', required=False, nargs=-1)
def remove_token(ctx, metadata_id, path, token):
    """Delete one to many tokens for a dataset"""


    if metadata_id is not None:
        path = metadata_id
    elif path is not None:
        path = path
    else:
        raise click.ClickException('Missing path or metadata_id')

    if delete_token(path, token):
        click.echo('Token successfully deleted')


auth.add_command(add_token)
auth.add_command(remove_token)
auth.add_command(has_access_dataset)
auth.add_command(has_access_path)
auth.add_command(is_restricted_dataset)
auth.add_command(is_restricted_path)
