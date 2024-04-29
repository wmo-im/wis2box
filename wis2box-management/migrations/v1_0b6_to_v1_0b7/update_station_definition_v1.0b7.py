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
import argparse
import csv
import json
import os
from pathlib import Path

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from wis2box.log import LOGGER, setup_logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
setup_logger(loglevel=LOG_LEVEL)

DATADIR = os.getenv("WIS2BOX_DATADIR")
THISDIR = os.path.dirname(os.path.realpath(__file__))

es_api = os.getenv("WIS2BOX_API_BACKEND_URL")
es_index = "stations"
station_file = Path(DATADIR) / "metadata" / "station" / "station_list.csv"


def apply_mapping(value, mapping):
    return mapping.get(value, value)  # noqa use existing value as default in case no match found


def apply_mapping_elastic(records, codelists, code_maps):
    updates = []
    for idx in range(len(records)):
        record = records[idx]['_source']
        # iterate over code lists and map entries
        for codelist in codelists:
            if codelist in record['properties']:
                record['properties'][codelist] = code_maps[codelist].get(
                    record['properties'][codelist],
                    record['properties'][codelist]  # noqa use existing value as default in case no match found
                )
            else:
                LOGGER.info(f"No matching code list found for {codelist}")
        # now update record for ES
        updates.append({
            "_op_type": "update",
            "_index": records[idx].get('_index'),
            "_id": records[idx].get('_id'),
            "doc": record
        })

    return updates


def migrate(dryrun: bool = False):
    # first load code lists / mappings
    code_maps = {}
    codelists = ('facility_type', 'territory_name', 'wmo_region')
    for codelist in codelists:
        LOGGER.info(f"Loading code list map for {codelist}")
        p = Path(THISDIR)
        mapping_file = p / "mapping_files" / f"{codelist}.json"
        try:
            with open(mapping_file) as fh:
                code_maps[codelist] = json.load(fh)
        except Exception as e:
            LOGGER.error(f"Error loading mapping file for {codelist}")
            raise e

    # First migrate / update data in station list CSV file
    # list to store stations
    stations = []
    # open station file and map
    LOGGER.info("Processing {station_file}")
    with open(station_file, 'r') as fh:
        try:
            reader = csv.DictReader(fh)
        except Exception as e:
            LOGGER.error("Error creating DictReader")
            raise e
        LOGGER.info("Iterating over rows")
        for idx, row in enumerate(reader):
            for codelist in codelists:
                if codelist in row:
                    try:
                        row[codelist] = apply_mapping(row.get(codelist),
                                                      code_maps.get(codelist))
                    except Exception as e:
                        LOGGER.error(f"Error processing {codelist} in row {idx}")  # noqa
                        raise e
                else:
                    pass
            stations.append(row)
    if len(stations)>0:
        if dryrun:
            LOGGER.info(
                f"dryrun == True, writing updated {station_file} to stdout")
            print(','.join(map(str, stations[0].keys())))
            for station in stations:
                print(','.join(map(str, station.values())))
        else:
            # now write data to file
            LOGGER.info(
                f"Writing updated {station_file} to {station_file}.v1.0b7")
            try:
                with open(f"{station_file}.v1.0b7", 'w') as fh:
                    columns = list(stations[0].keys())
                    writer = csv.DictWriter(fh, fieldnames=columns)
                    writer.writeheader()
                    for station in stations:
                        writer.writerow(station)
            except Exception as e:
                LOGGER.error("Error writing updated station file")
                raise e
    else:
        LOGGER.info("No stations in station_list.csv to be updated")

    # now migrate ES data
    # Get elastic search connection
    LOGGER.info("Updating station data in Elasticsearch index")
    LOGGER.info("Connecting to API ...")
    try:
        es = Elasticsearch(es_api)
    except Exception as e:
        LOGGER.error(f"Error connecting to {es_api}")
        raise e

    more_data = True  # flag to keep looping until all data processed
    batch_size = 100  # process in batch sizes of 100
    cursor = 0  # cursor to keep track of position

    LOGGER.info(f"Processing stations in batches of {batch_size}")
    # now loop until all data processed
    while more_data:
        try:
            res = es.search(index=es_index,
                            query={'match_all': {}},
                            size=batch_size,
                            from_=cursor)
        except Exception as e:
            LOGGER.error(f"Error fetching data from {es_index}")
            raise e
        nhits = len(res['hits']['hits'])
        LOGGER.info(f"Processing {nhits} stations")
        cursor += batch_size
        if nhits < batch_size:
            more_data = False
        stations = res['hits']['hits']
        LOGGER.info("Applying mappings ...")
        try:
            updates = apply_mapping_elastic(stations, codelists, code_maps)
        except Exception as e:
            LOGGER.error("Error applying mappings")
            raise e
        if dryrun:
            LOGGER.info("dryrun == True, writing updates to stdout")
            print(updates)
        else:
            LOGGER.info("Updating index ...")
            try:
                bulk(es, updates)
            except Exception as e:
                LOGGER.error("Error applying bulk update")
                raise e


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dryrun',
                        action='store_true',
                        help='Run in dry run mode (output to stdout)')
    args = parser.parse_args()
    # Execute
    LOGGER.info("Running wis2box migration from v1_0b6 to v1_0b7 (update station definitions)")  # noqa
    migrate(dryrun=args.dryrun)
