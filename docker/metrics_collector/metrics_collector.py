#!/usr/bin/env python
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
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_uncollectable_total'])
#REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])

WIS2BOX_LOGGING_LOGLEVEL = os.environ.get('WIS2BOX_LOGGING_LOGLEVEL')
# gotta log to stdout so docker logs sees the python-logs
logging.basicConfig(stream=sys.stdout)
# create our own logger using same log-level as wis2box
logger = logging.getLogger('metrics_collector')
logger.setLevel(WIS2BOX_LOGGING_LOGLEVEL)

INTERRUPT = False

def collect_file_data_by_topic(root,filematch):
    """
    helper-function to collect data using labels 'topic' from given root-path and file-type
    """
    from fnmatch import fnmatch
    data = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name,filematch):
                topic = '.'.join(path.replace(root,'').split('/')[2:]) if 'public' in root else '.'.join(path.replace(root,'').split('/')[1:]) 
                size = os.stat(os.path.join(path, name)).st_size
                if topic in data:
                    data[topic]['size'] += size
                    data[topic]['file_count'] += 1
                else :  
                    data[topic] = {}
                    data[topic]['size'] = size
                    data[topic]['file_count'] = 1
    return data

def gather_file_metrics():
    """
      gather file metrics by checking content of wis2box public directory
    """    
    bufr_public_nrfile_gauge = Gauge('bufr4_public_nrfile', 'Number of bufr4 in /data/public')
    bufr_public_nrfile_by_topic_gauge = Gauge('bufr4_public_nrfile_by_topic', 'Number of bufr4 in /data/public, by topic',["topic"])
    bufr_public_bytes_gauge = Gauge('bufr4_public_bytes', 'Bytes used by bufr4 stored in /data/public')
    bufr_public_bytes_by_topic_gauge = Gauge('bufr4_public_bytes_by_topic', 'Bytes used by bufr4 stored in /data/public, by topic',["topic"])

    csv_incoming_nrfile_gauge = Gauge('csv_incoming_nrfile', 'Number of csv in /data/incoming')
    csv_incoming_nrfile_by_topic_gauge = Gauge('csv_incoming_nrfile_by_topic', 'Number of csv in /data/incoming, by topic', ["topic"])
    csv_incoming_bytes_gauge = Gauge('csv_incoming_bytes', 'Bytes used by csv stored in /data/incoming')
    csv_incoming_bytes_by_topic_gauge = Gauge('csv_incoming_bytes_by_topic', 'Bytes used by csv stored in /data/incoming, by topic', ["topic"])
    
    
    while INTERRUPT == False:
        # count bufr4 in outgoing directory
        bufr_public_files = 0
        bufr_public_bytes = 0
        root_public = '/data/wis2box/data/public'
        bufr_data = collect_file_data_by_topic(root_public,filematch='*.bufr4')
        logger.info(f"Update metrics for bufr, {len(bufr_data)} topics found in {root_public}")
        for topic in bufr_data.keys() :
            bufr_public_nrfile_by_topic_gauge.labels(topic).set(bufr_data[topic]['file_count'])
            bufr_public_bytes_by_topic_gauge.labels(topic).set(bufr_data[topic]['size'])
            bufr_public_files += bufr_data[topic]['file_count']
            bufr_public_bytes += bufr_data[topic]['size']
        # update general bufr4-stat-gauges
        bufr_public_nrfile_gauge.set(bufr_public_files)
        bufr_public_bytes_gauge.set(bufr_public_bytes)
        
        # count csv in coming directory
        csv_incoming_files = 0
        csv_incoming_bytes = 0
        root_incoming = '/data/wis2box/data/incoming'
        csv_data = collect_file_data_by_topic(root_incoming,filematch='*.csv')
        logger.info(f"Update metrics for csv, {len(csv_data)} topics found in {root_incoming}")
        for topic in csv_data.keys() :
            csv_incoming_nrfile_by_topic_gauge.labels(topic).set(csv_data[topic]['file_count'])
            csv_incoming_bytes_by_topic_gauge.labels(topic).set(csv_data[topic]['size'])
            csv_incoming_files += csv_data[topic]['file_count']
            csv_incoming_bytes += csv_data[topic]['size']
        # update general csv-stat-gauges
        csv_incoming_nrfile_gauge.set(csv_incoming_files)
        csv_incoming_bytes_gauge.set(csv_incoming_bytes)

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