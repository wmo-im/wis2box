# wis2box

[![Tests](https://github.com/wmo-im/wis2box/workflows/tests%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/wis2box/actions/workflows/tests.yml)
[![Docs](https://github.com/wmo-im/wis2box/workflows/docs/badge.svg)](https://github.com/wmo-im/wis2box/actions/workflows/docs.yml)

## WIS 2.0 in a box

WIS 2.0 in a box provides a platform with the capabilities for centres to
integrate their data holdings and publish them to the WMO Information System
with a plug and play capability supporting data publishing, discovery
and access.

## Installation

```bash
python3 -m venv wis2box
cd wis2box
git clone https://github.com/wmo-im/wis2box.git
cd wis2box

# setup local environment variables
cp wis2box.env dev.env
# edit/adjust accordingly
vi dev.env
```

## Deploying with Docker Compose

```bash
# wi2node-ctl options
python3 wis2box-ctl.py

# view docker config
python3 wis2box-ctl.py config

# build local images
python3 wis2box-ctl.py build

# start system
python3 wis2box-ctl.py start

# login to main wis2box container
python3 wis2box-ctl.py login

# restart containers
python3 wis2box-ctl.py restart

# view upstatus
python3 wis2box-ctl.py status -a

# view logs
python3 wis2box-ctl.py  logs

# stop system
python3 wis2box-ctl.py  stop

# update images
python3 wis2box-ctl.py  update

# redeploy containers
python3 wis2box-ctl.py  up
```

## Running

- Note: run `python3 wis2box-ctl.py login` first to access the container

From command line:

```bash
# fetch version
wis2box --version

# create environment
wis2box environment create

# show environment
wis2box environment show

# create dataset topic hierarchy directories
wis2box data setup --topic-hierarchy foo.bar.baz

# display dataset topic hierarchy and directories
wis2box data info --topic-hierarchy foo.bar.baz

# process incoming data with topic hierarchy
wis2box data ingest --topic-hierarchy foo.bar.baz -p /path/to/file.csv

# process incoming data (manually/no PubSub); topic hierarchy is inferred
# from fuzzy filepath equivalent
wis2box data ingest -p /path/to/foo/bar/baz/data/file.csv

# create discovery metadata control file (MCF)
# pygeometa MCF reference: https://geopython.github.io/pygeometa/reference/mcf
vi $WIS2BOX_DATADIR/data/config/foo/bar/baz/discovery-metadata.yml

# create CSV of stations
# format:
# station_name,wigos_station_identifier
vi /path/to/station_list.csv

# cache station metadata from OSCAR/Surface from a CSV of station name/WSI records
wis2box metadata station cache /path/to/station_list.csv

# publish station metadata to WMO OSCAR/Surface
wis2box metadata station publish $WIS2BOX_DATADIR/metadata/station/1.yml
wis2box metadata station publish $WIS2BOX_DATADIR/metadata/station/2.yml
wis2box metadata station publish $WIS2BOX_DATADIR/metadata/station/3.yml

# generate local station collection GeoJSON for pygeoapi publication
wis2box metadata station publish-collection

# publish dataset discovery metadata to local catalogue
wis2box metadata discovery publish foo/bar/baz

# unpublish discovery metadata to local catalogue
wis2box metadata discovery unpublish foo/bar/baz

# add collection to wis2box API backend and api config from mcf
wis2box api add-collection $WIS2BOX_DATADIR/data/config/foo/bar/baz/discovery-metadata.yml --topic-hierarchy foo.bar.baz

# add processed GeoJSON in public folder to wis2box API backend
wis2box api add-collection-items --topic-hierarchy foo.bar.baz

# delete collection from wis2box API backend and config
wis2box api delete-collection --topic-hierarchy foo.bar.baz

# clean data
wis2box data clean --days 30

# archive data
wis2box data archive
```

## Development workflows

## Maintenance and code linting

```bash
# clean up dangling containers and images
python3 wis2box-ctl.py prune

# run a flake8 check on all Python code
python3 wis2box-ctl.py lint
```

### Running tests

```bash
# via setuptools
python3 setup.py test

# directly via pytest
pytest
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/wis2box/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
