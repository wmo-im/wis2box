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
from pathlib import Path

from wis2box.topic_hierarchy import validate_and_load

LOGGER = logging.getLogger(__name__)

# TODO ask Tom where this functionality should be hosted
def get_data(http_filepath: str):
    """
    get data from (local) storage
    """
    from wis2box.env import WIS2BOX_STORAGE_TYPE
    if WIS2BOX_STORAGE_TYPE == 'S3' :
        # TODO: get this from plugin-class ?
        from wis2box.storage.minio import MinioStorage as storage
        from wis2box.env import S3_ROOT_USER, S3_ROOT_PASSWORD, S3_ENDPOINT
        auth = {'username' : S3_ROOT_USER, 'password' : S3_ROOT_PASSWORD}
        storage_path = http_filepath.replace(S3_ENDPOINT+'/','')
        storage_name = storage_path.split('/')[0]
        file_identifier = storage_path.replace(storage_name,'')
        storage = storage(S3_ENDPOINT,storage_name,auth)
        return storage.get(file_identifier)
    else :
        # maybe add attempt to get data from public http using requests? 
        LOGGER.warning(f"No matching storage-endpoint found")
        return None

class Handler:
    def __init__(self, filepath: str , topic_hierarchy: str = None):
        self.filepath = filepath
        self.filetype = filepath.split(".")[-1]
        self.plugin = None

        if topic_hierarchy is not None:
            th = topic_hierarchy
            fuzzy = False
        else:
            th = self.filepath
            fuzzy = True

        try:
            self.topic_hierarchy, self.plugin = validate_and_load(th, self.filetype, fuzzy=fuzzy) # noqa
        except Exception as err:
            msg = f'Topic Hierarchy validation error: {err}'
            LOGGER.error(msg)
            raise ValueError(msg)

    def handle(self, notify=False) -> bool:
        try:
            if self.filepath[0:4] != 'http' :
                self.plugin.transform(self.filepath)
            else:
                self.plugin.transform(get_data(self.filepath),file_name=self.filepath.split('/')[-1])
            self.plugin.publish(notify)
        except Exception as err:
            msg = f'file {self.filepath} failed to transform/publish: {err}'
            LOGGER.warning(msg)
            return False
        return True

    def publish(self, backend) -> bool:
        index_name = self.topic_hierarchy.dotpath
        if self.filepath[0:4] != 'http' :
            with Path(self.filepath).open() as fh1:
                geojson = json.load(fh1)
                backend.upsert_collection_items(index_name, [geojson])
        else:
            geojson = json.load(get_data(self.filepath))
            backend.upsert_collection_items(index_name, [geojson])
        return True
