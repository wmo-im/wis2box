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
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from wis2box.api.process.base import BaseConfig
from wis2box.env import DOCKER_API_URL

LOGGER = logging.getLogger(__name__)


class PygeoapiProcess(BaseConfig):
    """Abstract API config"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
        """

        super().__init__(defs)
        self.url = f'{DOCKER_API_URL}/processes'
        self.http = Session()
        retry_strategy = Retry(
            total=4,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=2,
            method_whitelist=['GET', 'PUT', 'DELETE']
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount('https://', adapter)
        self.http.mount('http://', adapter)

    def execute(self, name: str, inputs: dict) -> dict:
        """
        Execute a process

        :param name: name of process
        :param input: `dict` of process inputs

        :returns: `dict` with result
        """
        synopUrl = f'{self.url}/{name}/execution'

        # Set headers
        headers = {
            'encode': 'json',
            'Content-Type': 'application/geo+json'
        }

        payload = {
            'inputs': inputs
        }

        # Make the asynchronous HTTP POST request
        response = self.http.post(synopUrl, headers=headers, json=payload)

        # Handle the response
        if response.status_code == 200:
            response_data = response.json()
            return response_data
        else:
            LOGGER.error(f"Request failed with status code {response.status_code}") # noqa
            return {}  # Return an appropriate response in case of failure

    def __repr__(self):
        return '<PygeoapiConfig>'
