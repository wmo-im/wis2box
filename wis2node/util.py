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

from base64 import b64encode
from datetime import date, datetime, time
from decimal import Decimal
import logging
import os
from pathlib import Path
import re
from typing import Iterator, Union
import yaml

LOGGER = logging.getLogger(__name__)


def get_typed_value(value) -> Union[float, int, str]:
    """
    Derive true type from data value

    :param value: value

    :returns: value as a native Python data type
    """

    try:
        if '.' in value:  # float?
            value2 = float(value)
        elif len(value) > 1 and value.startswith('0'):
            value2 = value
        else:  # int?
            value2 = int(value)
    except ValueError:  # string (default)?
        value2 = value

    return value2


def json_serial(obj: object) -> Union[bytes, str, float]:
    """
    helper function to convert to JSON non-default
    types (source: https://stackoverflow.com/a/22238613)

    :param obj: `object` to be evaluated

    :returns: JSON non-default type to `str`
    """

    if isinstance(obj, (datetime, date, time)):
        LOGGER.debug('Returning as ISO 8601 string')
        return obj.isoformat()
    elif isinstance(obj, bytes):
        try:
            LOGGER.debug('Returning as UTF-8 decoded bytes')
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            LOGGER.debug('Returning as base64 encoded JSON object')
            return b64encode(obj)
    elif isinstance(obj, Decimal):
        LOGGER.debug('Returning as float')
        return float(obj)
    elif isinstance(obj, Path):
        LOGGER.debug('Returning as path string')
        return str(obj)

    msg = f'{obj} type {type(obj)} not serializable'
    LOGGER.error(msg)
    raise TypeError(msg)


def walk_path(path: str, regex: str) -> Iterator[str]:
    """
    Walks os directory path collecting all CSV files.

    :param path: required, string. os directory.
    :param regex: required, string. regex pattern to match files

    :returns: list. List of csv filepaths.
    """

    reg = re.compile(regex)
    for root, _, files in os.walk(path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            if reg.match(filepath):
                yield filepath


def yaml_load(fh) -> dict:
    """
    serializes a YAML files into a pyyaml object

    :param fh: file handle

    :returns: `dict` representation of YAML
    """

    # support environment variables in config
    # https://stackoverflow.com/a/55301129
    path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')

    def path_constructor(loader, node):
        env_var = path_matcher.match(node.value).group(1)
        if env_var not in os.environ:
            msg = 'Undefined environment variable {} in config'.format(env_var)
            raise EnvironmentError(msg)
        return get_typed_value(os.path.expandvars(node.value))

    class EnvVarLoader(yaml.SafeLoader):
        pass

    EnvVarLoader.add_implicit_resolver('!path', path_matcher, None)
    EnvVarLoader.add_constructor('!path', path_constructor)

    return yaml.load(fh, Loader=EnvVarLoader)


def yaml_dump(fh: str, content: dict) -> None:
    """
    Writes serialized YAML to file

    :param fh: file handle
    :param content: dict, yaml file content

    :returns: `None`
    """
    return yaml.safe_dump(content, fh, sort_keys=False, indent=4)
