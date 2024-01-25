
import logging

from pathlib import Path
from datetime import datetime
from typing import Union

from wis2box.data.base import BaseAbstractData

LOGGER = logging.getLogger(__name__)


class MessageData(BaseAbstractData):
    """
    DataPublish:

    transform sets output_data to input_data
    using metadata received by the plugin
    """

    def __init__(self, defs: dict) -> None:
        self._meta = defs['_meta']
        # remove _meta from defs before passing to super
        defs.pop('_meta')
        super().__init__(defs)

    def transform(self, input_data: Union[Path, bytes],
                  filename: str = '') -> bool:
        """
        Transform input_data to output_data

        :param input_data: input data
        :param filename: filename of input data
        :param _meta: metadata of input data

        :returns: `bool` of result
        """

        suffix = filename.split('.')[-1]
        rmk = filename.split('.')[0]
        input_bytes = self.as_bytes(input_data)

        # convert isoformat to datetime
        self._meta['data_date'] = datetime.fromisoformat(self._meta['data_date']) # noqa
        # add relative filepath to _meta
        self._meta['relative_filepath'] = self.get_local_filepath(self._meta['data_date']) # noqa

        self.output_data[rmk] = {
            suffix: input_bytes,
            '_meta': self._meta
        }
        return True

    def get_local_filepath(self, date_):
        yyyymmdd = date_.strftime('%Y-%m-%d')
        return Path(yyyymmdd) / 'wis' / self.topic_hierarchy.dirpath
