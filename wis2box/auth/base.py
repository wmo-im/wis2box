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

import hashlib
import hmac
import logging
import os
import sqlite3
from typing import Iterable, Tuple

LOGGER = logging.getLogger(__name__)


def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """

    salt = os.urandom(24)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """

    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


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
            s = 'CREATE TABLE IF NOT EXISTS auth (salt text PRIMARY KEY, key text NOT NULL, topic text NOT NULL)'  # noqa
            conn.execute(s)

    def topics(self) -> Iterable[str]:
        try:
            with SQLite3Backend(self.db) as conn:
                s = 'SELECT DISTINCT topic FROM auth'
                for row in conn.execute(s):
                    yield dict(row).get('topic')

        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

    def _yield(self, key, th) -> str:
        """
        Yields a key's salt for a topic hierarchy

        :param key: key
        :param th: topic hierarchy

        :returns: `str` salt of authenticatied token
        """

        try:
            with SQLite3Backend(self.db) as conn:
                s = 'SELECT * FROM auth WHERE topic=:th'
                for row in conn.execute(s, {'th': th}):
                    rd = dict(row)
                    if is_correct_password(rd['salt'], rd['key'], key):
                        return rd['salt']

        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

    def is_resource_open(self, th) -> bool:
        """
        Checks to see if resource has access control configured

        :param th: topic hierarchy

        :returns: `bool` of result
        """
        return False if th in self.topics() else True

    def is_token_authorized(self, key, th) -> bool:
        """
        Validates a tokens access to a topic

        :param key: key
        :param th: topic hierarchy

        :returns: `bool` of result
        """
        return True if self._yield(key, th) else False

    def add(self, key, th) -> bool:
        """
        Adds a token and topic

        :param key: key
        :param th: topic hierarchy

        :returns: `bool` of result
        """
        salt, pw_hash = hash_new_password(key)
        try:
            with SQLite3Backend(self.db) as conn:
                s = 'INSERT INTO auth (salt, key, topic) VALUES (?, ?, ?)'
                conn.execute(s, (salt, pw_hash, th))
        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

        return True

    def delete_by_token(self, key, th) -> bool:
        """
        Adds a token and topic

        :param key: key
        :param th: topic hierarchy

        :returns: `bool` of result
        """

        salt = self._yield(key, th)

        try:
            with SQLite3Backend(self.db) as conn:
                conn.execute('DELETE FROM auth WHERE salt=:salt',
                             {'salt': salt})
        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

        return True

    def delete_by_topic_hierarchy(self, th) -> bool:
        """
        Adds a token and topic

        :param key: key
        :param salt: salt
        :param topic: topic

        :returns: `bool` of result
        """

        try:
            with SQLite3Backend(self.db) as conn:
                conn.execute('DELETE FROM auth WHERE topic=:th', {'th': th})
        except sqlite3.IntegrityError as err:
            msg = f'Insert error: {err}'
            LOGGER.error(msg)

        return True
