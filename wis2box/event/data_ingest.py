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
import os
from pathlib import Path

from sarracenia import Message
from sarracenia.flowcb import FlowCB

from wis2box.handler import Handler

LOGGER = logging.getLogger(__name__)


class Event(FlowCB):
    def __init__(self, options):
        self.options = options

    def after_accept(self, worklist):
        new_incoming = []
        for incoming_message in worklist.incoming:

            filepath = (Path('/') / incoming_message['relPath'])

            LOGGER.debug(f'Incoming filepath: {filepath}')

            try:
                LOGGER.debug(f'Processing {filepath}')
                handler = Handler(filepath)
                if handler.handle():
                    LOGGER.debug('Data processed')
                    for filepath_out in handler.plugin.files():
                        LOGGER.debug(f'Public filepath: {filepath_out}')
                        message = Message.fromFileData(
                            filepath_out,
                            self.options,
                            os.stat(filepath_out)
                        )
                        new_incoming.append(message)
            except ValueError as err:
                msg = f'handle() error: {err}'
                LOGGER.error(msg)

            worklist.incoming = new_incoming
