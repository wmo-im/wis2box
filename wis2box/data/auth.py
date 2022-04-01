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
import os.path
import sqlite3

from wis2box.env import AUTH_STORE

LOGGER = logging.getLogger(__name__)


class SQLite3Backend:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row

        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()


class BaseAuth:
    """Abstract authentication / authorization"""
    def __init__(self, db: str) -> None:
        """
        Abstract authentication / authorization

        :param db: path to auth db

        :returns: `None`
        """

        self.db = db

        if not os.path.exists(self.db):
            self.setup()

    def setup(self) -> bool:
        """
        Database init

        :returns: `bool` of result
        """

        with SQLite3Backend(self.db) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS auth (key text PRIMARY KEY, topic text NOT NULL)')  # noqa

    def add(self, key, topic) -> bool:
        """
        Adds a token and topic

        :param key: key
        :param topic: topic

        :returns: `bool` of result
        """

        try:
            with SQLite3Backend(self.db) as conn:
                conn.execute('INSERT INTO auth (key, topic) VALUES (?, ?)',
                             (key, topic))
        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

        return True


@click.group()
def auth():
    """Auth workflow"""
    pass


# auth.add_command(some_command)
