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
from pathlib import Path
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from wis2box import cli_helpers
from wis2box.api import setup_collection
from wis2box.event.messages import gcm
from wis2box.handler import Handler

LOGGER = logging.getLogger(__name__)


class Watchpuppy:
    """
    Class combining watchdog with publish-to-mqtt
    """

    def __init__(self):
        self.observer = Observer()

        self.event_handler = PatternMatchingEventHandler(
            patterns=['.*'],
            ignore_patterns=[],
            ignore_directories=True)

        self.event_handler.on_created = self.on_created

    def run(self, path: Path, polling_interval: int):
        """
        Run watch

        :param path: `Path` directory path
        :param polling_interval: `int` polling interval

        :returns: `None`
        """

        LOGGER.info(f'Starting watchdog-observer on path={path}')
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()
        try:
            while True:
                msg = f'Heartbeat {time.strftime("%Y-%m-%dT%H:%M:%SZ")}'
                LOGGER.debug(msg)
                time.sleep(polling_interval)
        except Exception as err:
            LOGGER.error(f'Observing error: {err}')
            self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        LOGGER.debug(f'Incoming event path: {event.src_path}')

        LOGGER.info(f'Received file: {event.src_path}')
        try:
            LOGGER.info(f'Processing {event.src_path}')
            handler = Handler(event.src_path)
            if handler.handle():
                LOGGER.info('Data processed')

        except ValueError as err:
            msg = f'handle() error: {err}'
            LOGGER.error(msg)
        except Exception as err:
            msg = f'handle() error: {err}'
            raise err


@click.command()
@click.pass_context
@cli_helpers.OPTION_PATH
@click.option('--interval', '-i', help='Polling interval', default=5)
@cli_helpers.OPTION_VERBOSITY
def watch(ctx, path, interval, verbosity):
    """Subscribe to a broker/topic"""
    click.echo('Adding messages collection')
    setup_collection(meta=gcm())

    LOGGER.info(f"Listening to {path} every {interval} second")  # noqa

    w = Watchpuppy()
    w.run(path=path, polling_interval=int(interval))
