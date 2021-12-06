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

import json
import logging

from tinydb import where, Query, TinyDB

from wis2node.env import CATALOGUE_BACKEND

LOGGER = logging.getLogger(__name__)


def upsert_metadata(record: str) -> None:
    """
    Upserts record metadata into catalogue

    :param record: `str` of record metadata

    :returns: None
    """

    rec_dict = json.loads(record)

    LOGGER.info(f'Connecting to catalogue {CATALOGUE_BACKEND}')
    db = TinyDB(CATALOGUE_BACKEND)

    record_query = Query()

    try:
        res = db.upsert(rec_dict, record_query.id == rec_dict['id'])
        LOGGER.info(f"Record {rec_dict['id']} upserted with internal id {res}")
    except Exception as err:
        LOGGER.error(f'record insertion failed: {err}', exc_info=1)
        raise

    return


def delete_metadata(identifier: str) -> None:
    """
    Deletes a discovery metadata record from the catalogue

    :param identifier: `str` of metadata record identifier

    :returns: None
    """

    db = TinyDB(CATALOGUE_BACKEND)
    db.remove(where('id') == identifier)
