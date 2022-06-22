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

from datetime import datetime
import logging
from pathlib import Path
import time

import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from wis2box import cli_helpers
from wis2box.env import BROKER, BROKER_TYPE
from wis2box.plugin import load_plugin, PLUGINS
from wis2box.pubsub.topics import Topics

LOGGER = logging.getLogger(__name__)


class Watcher:
    """
    Generic watcher class
    """

    def __init__(self):
        self.observer = Observer()

    def run(self, path: Path, polling_interval: int):
        """
        Run watch

        :param path: `pathlib.Path` of directory path
        :param polling_interval: `int` of polling interval

        :returns: `None`
        """

        LOGGER.debug('Starting observer')
        event_handler = Handler()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        try:
            while True:
                now = datetime.now().isoformat()
                LOGGER.debug(f'Heartbeat {now}')
                time.sleep(polling_interval)
        except Exception as err:
            LOGGER.error(f'Observing error: {err}')
            self.observer.stop()

        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Generic watch handler
    """

    @staticmethod
    def on_created(event):
        LOGGER.debug(f'Incoming event path: {event.src_path}')
        if event.is_directory:
            LOGGER.debug('Not a file; skipping')
            return None

        LOGGER.info(f'Received file: {event.src_path}')
        LOGGER.info('Advertising to broker')

        defs = {
            'codepath': PLUGINS['pubsub'][BROKER_TYPE]['plugin'],
            'url': BROKER
        }

        broker = load_plugin('pubsub', defs)

        from wis2box.pubsub.message import Sarracenia_v03Message
        s = Sarracenia_v03Message(event.src_path)
        s.prepare()

        topic = f'xlocal/v03{s.filepath.parent}'
        broker.pub(topic, s.dumps())


@click.command()
@click.pass_context
@cli_helpers.OPTION_PATH
@click.option('--polling_interval', '-pi', type=int, default=5,
              help='Polling interval')
@cli_helpers.OPTION_VERBOSITY
def watch(ctx, path, verbosity, polling_interval=5):
    """Watch a directory for new files"""
    click.echo(f"Listening to {path} every {polling_interval} second{'s'[:polling_interval^1]}")  # noqa
    w = Watcher()
    w.run(path, polling_interval)
