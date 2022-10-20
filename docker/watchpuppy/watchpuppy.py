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
import json
import logging
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlparse

import paho.mqtt.publish as publish
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
LOGGER = logging.getLogger('watchpuppy')
LOGGER.setLevel(LOGGING_LOGLEVEL)
logging.basicConfig(stream=sys.stdout)

WATCHPATH = os.environ.get('WATCHPATH', '')
POLLING_INTERVAL = os.environ.get('POLLING_INTERVAL', 5)
FILE_PATTERNS = os.environ.get('FILE_PATTERNS', '*.*')
TOPIC_BASE = 'xlocal/v03'

BROKER_HOST = os.environ.get('WIS2BOX_BROKER_HOST', '')
BROKER_USERNAME = os.environ.get('WIS2BOX_BROKER_USERNAME', '')
BROKER_PASSWORD = os.environ.get('WIS2BOX_BROKER_PASSWORD', '')
BROKER_PORT = os.environ.get('WIS2BOX_BROKER_PORT', 1883)

BROKER = f'mqtt://{BROKER_USERNAME}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}'  # noqa


class NotMQTTException(Exception):
    """Raised when schema provided by broker-url is not mqtt or mqtts"""
    pass


class WatchpuppyMessage:
    def __init__(self, filepath):
        """
        Initializer

        :param filepath: path to data file/object

        :returns: `WatchpuppyMessage`
        """

        self.type = 'default-message'
        self.filepath = Path(filepath)
        self.message = {}
        self.message['relPath'] = self.filepath.as_posix()
        self.message['baseUrl'] = 'file:/'

    def prepare(self):
        self.message['pubtime'] = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
        self.message['size'] = self.filepath.stat().st_size

    def dumps(self) -> str:
        """
        Return string representation of message

        :returns: `str` of message content
        """

        return json.dumps(self.message)


class Watchpuppy:
    """
    Class combining watchdog with publish-to-mqtt
    """

    def __init__(self, broker_conn_string: str):
        self.mqtt_port = 1883
        self.observer = Observer()
        file_patterns = FILE_PATTERNS.split(',')
        LOGGER.info(f'Init event-handler on patterns: {file_patterns}')

        self.event_handler = PatternMatchingEventHandler(
            patterns=file_patterns,
            ignore_patterns=[],
            ignore_directories=True)

        self.event_handler.on_created = self.on_created

        # check if the broker_conn_string refers to an mqtt-connection-string
        broker_url = urlparse(broker_conn_string)
        if broker_url.scheme == 'mqtts':
            self.mqtt_port = 8883
        elif broker_url.scheme != 'mqtt':
            raise NotMQTTException

        self.broker_url = broker_url

    def run(self, path: Path, polling_interval: int):
        """
        Run watch

        :param path: `pathlib.Path` of directory path
        :param polling_interval: `int` of polling interval

        :returns: `None`
        """

        LOGGER.info(f'Starting watchdog-observer on path={path}')
        self.observer.schedule(self.event_handler, path, recursive=True)
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

    def on_created(self, event):
        LOGGER.debug(f'Incoming event path: {event.src_path}')

        LOGGER.info(f'Received file: {event.src_path}')
        LOGGER.info('Advertising to broker')

        try:
            msg = WatchpuppyMessage(event.src_path)
            msg.prepare()
            topic = f'{TOPIC_BASE}{msg.filepath.parent}'
            LOGGER.info(f'Publish msg={msg.dumps()} on topic={topic}')
            publish.single(
                topic=topic,
                payload=msg.dumps(),
                hostname=self.broker_url.hostname,
                port=self.mqtt_port,
                auth={
                    'username': self.broker_url.username,
                    'password': self.broker_url.password}
            )
        except Exception as err:
            LOGGER.error(f'Publishing error: {err}')


def main():
    # watch-puppy: watches and publishes events
    """
    Watch a directory for new files and publish a message when file is seen
    """

    LOGGER.info(f"Listening to {WATCHPATH} every {POLLING_INTERVAL} second")  # noqa

    w = Watchpuppy(broker_conn_string=BROKER)
    w.run(path=WATCHPATH, polling_interval=int(POLLING_INTERVAL))
    w.disconnect()


if __name__ == '__main__':
    main()
