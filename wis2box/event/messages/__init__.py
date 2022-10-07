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


"""Message module containing the plugins wrapping messages"""


def gcm() -> dict:
    """
    Gets collection metadata for API provisioning

    :returns: `dict` of collection metadata
    """

    return {
        'id': 'messages',
        'type': 'feature',
        'title': 'Data notifications',
        'description': 'Data notifications',
        'keywords': ['wmo', 'wis 2.0'],
        'bbox': [-180, -90, 180, 90],
        'links': ['https://example.org'],
        'id_field': 'id',
        'time_field': 'pubTime',
        'title_field': 'id',
    }
