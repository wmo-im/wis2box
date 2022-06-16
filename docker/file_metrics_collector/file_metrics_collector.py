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

import os
import time

from prometheus_client import start_http_server, Gauge

import logging
import sys

# de-register default-collectors
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# remove python-garbage-collectior metrics
REGISTRY.unregister(
    REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])

WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own logger using same log-level as wis2box
logger = logging.getLogger('file_metrics_collector')
logger.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

INTERRUPT = False


def collect_data(root, filematch):
    """
    helper-function to collect data on files in given root-path

    :param root: root-path for file search
    :param filematch: string to be contained in filename

    :returns: array of objects with file-data
    """
    from fnmatch import fnmatch
    data = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name, filematch):
                # parse wigos-id out of file-name
                # this will fail when files are formatted differently
                wsi = ''
                if 'WIGOS_' in name:
                    wsi = name.split('WIGOS_')[1].split(
                        f'_{time.strftime("%Y")}')[0]
                if wsi not in data:
                    data[wsi] = {}
                    data[wsi]['nfiles'] = 1
                else:
                    data[wsi]['nfiles'] += 1
    return data


def gather_file_metrics():
    """
    gather file metrics by checking content of wis2box data directory

    :returns: `None`
    """
    # Gauges to measure files counted in path
    bufr_out_nfile_total = Gauge(
        'bufr_out_nrfile_total',
        'Total bufr4 in /data/public')
    bufr_out_nfile_wsi_total = Gauge(
        'bufr_out_nrfile_wsi_total',
        'Total bufr4 in /data/public, by WIGOS-ID',
        ["wigos_id"])
    csv_in_nfile_total = Gauge(
        'csv_in_nrfile_total',
        'Total csv in /data/incoming')
    csv_in_nfile_wsi_total = Gauge(
        'csv_in_nrfile_wsi_total',
        'Total csv in /data/incoming, by WIGOS-ID',
        ["wigos_id"])

    while not INTERRUPT:
        # count bufr4 in outgoing directory
        root_public = '/data/wis2box/data/public'
        bufr_data = collect_data(root_public, filematch='*.bufr4')

        bufr_out_nfiles = 0
        for wigos_id in bufr_data:
            bufr_out_nfiles += bufr_data[wigos_id]['nfiles']
            bufr_out_nfile_wsi_total.labels(wigos_id).set(
                bufr_data[wigos_id]['nfiles']
            )
        logger.info(f"Found {bufr_out_nfiles} .bufr4 in {root_public}")
        # update gauge for total
        bufr_out_nfile_total.set(bufr_out_nfiles)

        # count csv in coming directory
        root_incoming = '/data/wis2box/data/incoming'
        csv_data = collect_data(root_incoming, filematch='*.csv')
        csv_in_nfiles = 0
        for wigos_id in csv_data:
            csv_in_nfiles += csv_data[wigos_id]['nfiles']
            csv_in_nfile_wsi_total.labels(wigos_id).set(
                csv_data[wigos_id]['nfiles']
            )
        logger.info(f"Found {len(csv_data)} .csv in {root_incoming}")
        # update gauge for total
        csv_in_nfile_total.set(csv_in_nfiles)

        # check again in X seconds
        X = 30
        logger.debug(f"Now sleep for {X} seconds !")
        time.sleep(X)


def main():
    start_http_server(8000)
    # this will loop forever
    gather_file_metrics()


if __name__ == '__main__':
    main()
