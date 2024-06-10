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
import requests

from wis2box import cli_helpers

LOGGER = logging.getLogger(__name__)

DOWNLOAD_URL = 'http://wis2downloader:5000'


@click.group()
def downloader():
    """Interact with the wis2downloader"""
    pass


@click.command('list-subscriptions')
@click.pass_context
@cli_helpers.OPTION_VERBOSITY
def list_subscriptions(ctx, verbosity):
    """list all subscriptions"""

    # make a GET requests to http://{DOWNLOAD_URL}/subscriptions
    try:
        response = requests.get(f'{DOWNLOAD_URL}/subscriptions')
        # check response status
        if response.status_code == 200:
            click.echo('Current subscriptions:')
            click.echo(response.text)
        else:
            click.echo(f'Error: {response.status_code}')
            click.echo(response.text)
    except requests.exceptions.ConnectionError:
        click.echo('Error: Connection refused')
        click.echo(f'Is the wis2downloader running on {DOWNLOAD_URL}?')


@click.command('add-subscription')
@click.pass_context
@click.option('--topic', '-t', help='The topic to subscribe to', required=True)
def add_subscription(ctx, topic):
    """add a subscription"""

    topic.replace('#', '%23')
    topic.replace('+', '%2B')
    # make a POST request to http://{DOWNLOAD_URL}/subscriptions
    try:
        response = requests.post(f'{DOWNLOAD_URL}/subscriptions?topic={topic}')
        # check response status
        if response.status_code == 200:
            click.echo('Subscription added')
            click.echo('Current subscriptions:')
            click.echo(response.text)
        else:
            click.echo('Subscription not added')
            click.echo(f'Error: {response.status_code}')
            click.echo(response.text)
    except requests.exceptions.ConnectionError:
        click.echo('Error: Connection refused')
        click.echo(f'Is the wis2downloader running on {DOWNLOAD_URL}?')


@click.command('remove-subscription')
@click.pass_context
@click.option('--topic', '-t', help='The topic to subscribe to', required=True)
def remove_subscription(ctx, topic):
    """remove a subscription"""

    topic.replace('#', '%23')
    topic.replace('+', '%2B')
    # make a DELETE request to http://{DOWNLOAD_URL}/subscriptions
    try:
        response = requests.delete(f'{DOWNLOAD_URL}/subscriptions?topic={topic}')  # noqa
        # check response status
        if response.status_code == 200:
            click.echo('Subscription deleted')
            click.echo('Current subscriptions:')
            click.echo(response.text)
        else:
            click.echo('Subscription not deleted')
            click.echo(f'Error: {response.status_code}')
            click.echo(response.text)
    except requests.exceptions.ConnectionError:
        click.echo('Error: Connection refused')
        click.echo(f'Is the wis2downloader running on {DOWNLOAD_URL}?')


downloader.add_command(list_subscriptions)
downloader.add_command(add_subscription)
downloader.add_command(remove_subscription)
