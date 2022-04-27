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
from time import sleep

from prometheus_client import start_http_server, Gauge

import logging
import sys

# de-register default-collectors
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# remove python-gargage-collectior metrics
REGISTRY.unregister(
    REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])

WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own logger using same log-level as wis2box
logger = logging.getLogger('metrics_collector')
logger.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

INTERRUPT = False


def collect_file_data_topic(root, filematch):
    """
    helper-function to collect data using labels 'topic'

    :param root: root-path for file search
    :param filematch: string to be contained in filename

    :returns: dictionary with topic as key
    """
    from fnmatch import fnmatch
    data = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name, filematch):
                topic = ''
                if 'public' in root:
                    topic = '.'.join(path.replace(root, '').split('/')[2:])
                else:
                    topic = '.'.join(path.replace(root, '').split('/')[1:])
                size = os.stat(os.path.join(path, name)).st_size
                if topic in data:
                    data[topic]['size'] += size
                    data[topic]['file_count'] += 1
                else:
                    data[topic] = {}
                    data[topic]['size'] = size
                    data[topic]['file_count'] = 1
    return data


def gather_file_metrics():
    """
    gather file metrics by checking content of wis2box public directory

    :returns: `None`
    """
    bufr_out_nrfile_gauge = Gauge('bufr4_out_nrfile',
                                  'Nr of bufr4 in /data/public')
    bufr_out_nrfile_topic_gauge = Gauge('bufr4_out_nrfile_topic',
                                        'Nr bufr4 in /data/public, by topic',
                                        ["topic"])
    bufr_out_bytes_gauge = Gauge('bufr4_out_bytes',
                                 'Bytes bufr4 stored in /data/public')
    bufr_out_bytes_topic_gauge = Gauge('bufr4_out_bytes_topic',
                                       'Bytes bufr4 in /data/public, by topic',
                                       ["topic"])

    csv_in_nrfile_gauge = Gauge('csv_in_nrfile',
                                'Number of csv in /data/incoming')
    csv_in_nrfile_topic_gauge = Gauge('csv_in_nrfile_topic',
                                      'Nr of csv in /data/incoming, by topic',
                                      ["topic"])
    csv_in_bytes_gauge = Gauge('csv_in_bytes',
                               'Bytes csv in /data/incoming')
    csv_in_bytes_topic_gauge = Gauge('csv_in_bytes_topic',
                                     'Bytes csv in /data/incoming, by topic',
                                     ["topic"])

    while not INTERRUPT:
        # count bufr4 in outgoing directory
        bufr_out_files = 0
        bufr_out_bytes = 0
        root_public = '/data/wis2box/data/public'
        bufr_data = collect_file_data_topic(root_public, filematch='*.bufr4')
        logger.info(f"Update metrics for bufr, {len(bufr_data)} topics found")
        for topic in bufr_data.keys():
            bufr_out_nrfile_topic_gauge.labels(topic).set(
                bufr_data[topic]['file_count'])
            bufr_out_bytes_topic_gauge.labels(topic).set(
                bufr_data[topic]['size'])
            bufr_out_files += bufr_data[topic]['file_count']
            bufr_out_bytes += bufr_data[topic]['size']
        # update general bufr4-stat-gauges
        bufr_out_nrfile_gauge.set(bufr_out_files)
        bufr_out_bytes_gauge.set(bufr_out_bytes)

        # count csv in coming directory
        csv_in_files = 0
        csv_in_bytes = 0
        root_incoming = '/data/wis2box/data/incoming'
        csv_data = collect_file_data_topic(root_incoming, filematch='*.csv')
        logger.info(f"Update metrics for csv, {len(csv_data)} topics found")
        for topic in csv_data.keys():
            csv_in_nrfile_topic_gauge.labels(topic).set(
                csv_data[topic]['file_count'])
            csv_in_bytes_topic_gauge.labels(topic).set(
                csv_data[topic]['size'])
            csv_in_files += csv_data[topic]['file_count']
            csv_in_bytes += csv_data[topic]['size']
        # update general csv-stat-gauges
        csv_in_nrfile_gauge.set(csv_in_files)
        csv_in_bytes_gauge.set(csv_in_bytes)

        # check again in X seconds
        X = 30
        logger.debug(f"Now sleep for {X} seconds !")
        sleep(X)


def main():
    start_http_server(8000)
    # this will loop forever
    gather_file_metrics()


if __name__ == '__main__':
    main()
