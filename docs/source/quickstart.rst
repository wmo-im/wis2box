.. _quickstart:

Quickstart
==========

Requirements and dependencies
-----------------------------

wis2box requires the following prior to installation:

.. csv-table::
   :header: Requirement,Version
   :align: left

   `Python`_,3.8 (or greater)
   `Docker Engine`_, 20.10.14 (or greater)
   `Docker Compose`_,1.29.2 (or greater)

If these are already installed, you can skip to installing wis2box.

- To install Python, follow `Python installation`_.
- To install Docker, follow `Docker Engine installation`_.
- To install Docker Compose, follow `Compose installation`_.

Successful installation can be confirmed by inspecting the versions on your system.

.. code-block:: bash

    docker version
    docker-compose version
    python3 -V

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


wis2box configuration
---------------------

Wis2box will read environment variables from dev.env. A baseline is provided in dev.env.example. Copy dev.env.example to dev.env

.. code-block:: bash

    cp config_examples/dev.env.example dev.env

And update it to suit your needs. *You must replace '/your/data/directory'* with a valid directory on your host.

Wis2box configuration requires a file data-mapping.yml. 

Baselines are provided in config_examples/ :

* config_examples/data-mappings.yml.example-synop-bufr, input is .bufr containing SYNOP observation-data
* config_examples/data-mappings.yml.example-synop-csv, input is .csv containing SYNOP observation-data

For example for publishing .bufr files with SYNOP data: 
Copy this file in the directory you defined for /your/data/directory/

.. code-block:: bash

    cp config_examples/data-mapping.yml.example-synop-bufr /your/data/directory/data-mappings.yml
    
Edit /your/data/directory/data-mappings.yml and change 'ISO3C_country.center_id.data.core.weather.surface-based-observations.SYNOP':
    
    * replace 'ISO3C_country' with your corresponding ISO 3166 alpha-3 code.
    * replace 'center_id' with the string identifying the center running the wis2node.

wis2box needs to have a station_list.csv that contains the stations you will process, an example is provided in config_example/station_list.csv.example
Copy this file in the directory you defined for /your/data/directory/

.. code-block:: bash

    cp config_examples/station_list.csv.example /your/data/directory/station_list.csv

And update the file for your stations.

To enable the wis2box-api and wis2box-ui to show your data disovery-metadata needs to be setup. You can setup a metadata-discovery file from the example

.. code-block:: bash

    cp config_examples/surface-weather-observations.yml /your/data/directory/surface-weather-observations.yml

And edit the file /your/data/directory/surface-weather-observations.yml to provide the correct metadata for your dataset:

* replace 'ISO3C_country.center_id.data.core.weather.surface-based-observations.SYNOP' with the topic you used in data-mappings.yml previously*

* text provided in title and abstract will be displayed in wis2box-ui *

* provide a valid bounding-box in bbox *

wis2box build
-------------

Please run the 'build'-command when setting up wis2box for the first time. This will start the process of building the wis2box containers from source.

.. code-block:: bash
    
    python3 wis2box-ctl.py build

This might take a while. 

wis2box start
-------------

Start wis2box with Docker Compose and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py status
    
Check that all services are running (and not unhealthy). If neccessary repeat the command until all services are up and running.

setup api publication
---------------------

Login to the wis2box-container

.. code-block:: bash
    
    python3 wis2box-ctl.py login

Setup observation data processing and API publication:
Note: $WIS2BOX_DATADIR binds to the $WIS2BOX_HOST_DATADIR sets up previously, allowing this commands to access the 'surface-weather-observations.yml' you've prepared.

.. code-block:: bash

    wis2box api add-collection --topic-hierarchy ISO3C_country.center_id.data.core.weather.surface-based-observations.SYNOP $WIS2BOX_DATADIR/surface-weather-observations.yml

Cache and publish station collection and discovery metadata to the API:

.. code-block:: bash

    wis2box metadata discovery publish $WIS2BOX_DATADIR/surface-weather-observations.yml
    wis2box metadata station sync $WIS2BOX_DATADIR/station_list.csv

Logout of wis2box container:

.. code-block:: bash

    exit

From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running.

Congratulations your wis2box is now setup!

data ingestion
--------------

You will want to test it by uploading data to the 'wis2box-incoming'-storage. 

To access the storage-component visit http://localhost:3000 in your web browser. The default username/password is minio/minio123

debugging
---------

Something's now working? The wis2box includes a local grafana-instance to help you collect and view logs and figure out what's wrong.

Visit http://localhost:8999 in your local web browser to view the local grafana instance.

wis2box-ui
----------

The wis2box includes a UI to view the data that has been ingested.

To explore your wis2box-ui visit http://localhost:8999 in your web browser. 

Not seeing any data for your datasets on the wis2box-ui ?
After data has been ingested for a station for the first time, you need to re-publish the stations collection to additionally include link relations to collections with observations published from that station:

.. code-block:: bash
    
    python3 wis2box-ctl.py login
    wis2box metadata station publish-collection
    exit




