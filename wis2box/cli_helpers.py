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

from pathlib import Path

import click

from wis2box.log import setup_logger

ARGUMENT_FILEPATH = click.argument('filepath', type=click.File())

OPTION_PATH = click.option('--path', '-p', required=True,
                           help='Path to file or directory',
                           type=click.Path(file_okay=True, dir_okay=True,
                                           path_type=Path))

OPTION_TOPIC_HIERARCHY = click.option('--topic-hierarchy', '-th',
                                      help='Topic hierarchy')


def OPTION_VERBOSITY(f):
    logging_options = ['ERROR', 'WARNING', 'INFO', 'DEBUG']

    def callback(ctx, param, value):
        if value is not None:
            setup_logger(loglevel=value)
        return True

    return click.option('--verbosity', '-v',
                        type=click.Choice(logging_options),
                        help='Verbosity',
                        callback=callback)(f)


def cli_callbacks(f):
    f = OPTION_VERBOSITY(f)
    return f
