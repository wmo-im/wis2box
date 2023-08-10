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

LOGGER = logging.getLogger(__name__)


class BaseConfig:
    """Abstract API config"""
    def __init__(self, defs: dict) -> None:
        """
        initializer

        :param defs: `dict` of connection parameters
        """

    def execute_process(self, name: str, inputs: dict) -> bool:
        """
        Execute a process

        :param name: name of process
        :param inputs: `dict` of process inputs

        :returns: `bool` of process result
        """

        raise NotImplementedError()

    def __repr__(self):
        return '<BaseConfig>'
