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

from urllib.parse import urlparse
import logging
from typing import Any, Callable

LOGGER = logging.getLogger(__name__)


class BasePubSubClient:
    """Abstract Pub/Sub client"""
    def __init__(self, broker: str) -> None:
        """
        Pub/Sub initializer

        :param broker: `str` of broker RFC1738 URL

        :returns: `None`
        """

        self.type = None
        self.broker = broker
        self.broker_url = urlparse(self.broker['url'])

    def pub(self, topic: str, message: str) -> bool:
        """
        Publish a message to a broker/topic

        :param topic: `str` of topic
        :param message: `str` of message

        :returns: `bool` of publish result
        """

        raise NotImplementedError()

    def sub(self, topic: str) -> None:
        """
        Subscribe to a broker/topic

        :param topic: `str` of topic

        :returns: `None`
        """

        raise NotImplementedError()

    def bind(self, event: str, function: Callable[..., Any]) -> None:
        """
        Binds an event to a function

        :param event: `str` of event name
        :param function: Python callable

        :returns: `None`
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BasePubSubClient>'
