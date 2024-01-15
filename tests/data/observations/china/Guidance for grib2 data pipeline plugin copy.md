# Guidance for grib2 data pipeline plugin

1. Related File
   /wis2box/wis2box-management/wis2box/data/universal.py
   /wis2box/tests/data/data-mappings.py

2. Source Code

   """create function: UniversalData，inherit wis2box.data.base.BaseAbstractData"""

   Implement the transform method and fill in the output_data property, returning True

   /wis2box/wis2box-management/wis2box/data/universal.py

```py
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
from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Union

from dateutil.parser import parse

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class UniversalData(BaseAbstractData):
    """Universal data"""

    def __init__(self, defs: dict) -> None:
        super().__init__(defs)

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:

        filename = Path(filename)
        LOGGER.debug('Procesing data')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Deriving datetime')
        match = self.validate_filename_pattern(filename.name)

        if match is None:
            msg = f'Invalid filename format: {filename} ({self.file_filter})'
            LOGGER.error(msg)
            raise ValueError(msg)
        try:
            date_time = match.group(1)
        except IndexError:
            msg = 'Missing date/time in filename pattern'
            LOGGER.error(msg)
            raise ValueError(msg)

        date_time = parse(date_time)

        rmk = filename.stem
        suffix = filename.suffix.replace('.', '')

        self.output_data[rmk] = {
            suffix: input_bytes,
            '_meta': {
                'identifier': rmk,
                'relative_filepath': self.get_local_filepath(date_time),
                'data_date': date_time
            }
        }

        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
```

3. Data-mappings.yml configures the topic hierarchy of the numerical prediction data (CMA as an example)
   /wis2box/tests/data/data-mappings.py

    ```yml
    data: 		
        cn-cma-babj.data.core.weather.prediction.forecast.short-range.probabilistic.global:
            plugins:
                grib2:
     """call grib2 data pipeline plugin to deal with CMA_GEPS grib2 data"""
                    - plugin: wis2box.data.universal.UniversalData
                      notify: true
                      buckets:
                        - ${WIS2BOX_STORAGE_INCOMING}
                      file-pattern: '^.*_(\d{8})\d{2}.*\.grib2$'
    ```

4. Test data list
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-024.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-036.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-048.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-060.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-072.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-084.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-096.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-108.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-120.grib2
    Z_NAFP_C_BABJ_20231207000000_P_CMA-GEPS-GLB-132.grib2