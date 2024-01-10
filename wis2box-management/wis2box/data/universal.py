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

        filename2 = Path(filename)
        LOGGER.debug('Procesing data')
        input_bytes = self.as_bytes(input_data)

        LOGGER.debug('Deriving datetime')

        match = re.search(self.file_filter, filename2.name)
        if match:
            date_time = match.group(1)
        else:
            LOGGER.debug('Could not derive date/time: using today\'s date')
            date_time = datetime.now()

        if date_time:
            date_time = parse(date_time)

        rmk = filename2.stem
        suffix = filename2.suffix.replace('.', '')

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
