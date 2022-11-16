.. _tldr:

Too Long Didn't Read
====================

For the truly impatient, this section summarizes the steps to required to run wis2box from example configurations.

Environment
-----------

wis2box passes environment variables from dev.env to its containers on startup.
An example file is provided in ``examples/config/wis2box.env``. 
Copy this file to your working directory, and update it to suit your needs.

.. code-block:: bash

   cp examples/config/wis2box.env dev.env

.. note::

   You must map ``WIS2BOX_HOST_DATADIR`` to the absolute path of directory on your host machine.


For terminals that support environment variables, it may be useful to also define environment variables locally.
For terminals that do not support environment variables, you will need to define the asolute path to your data directory.

.. code-block:: bash

   # source
   . dev.env
   # verify
   echo $WIS2BOX_HOST_DATADIR

Data mappings
-------------

To start processing your own data, you need to define a data mappings file.
Example mapping files are provided in examples/config:

* ``examples/config/synop-bufr-mappings.yml``, input is .bufr containing SYNOP observation-data
* ``examples/config/synop-csv-mappings.yml``, input is .csv containing SYNOP observation-data

To publish .bufr files of SYNOP data:

.. code-block:: bash

   cp examples/config/synop-bufr-mappings.yml $WIS2BOX_HOST_DATADIR/data-mappings.yml

Edit ``$WIS2BOX_HOST_DATADIR/data-mappings.yml`` and change ``[iso3c_country].[center_id].data.core.weather.surface-based-observations.SYNOP``:

   * replace ``iso3c_country`` with your corresponding ISO 3166 alpha-3 code.
   * replace ``center_id`` with the string identifying the center running the wis2node.


Station metadata
----------------

wis2box needs to have a station_list.csv that contains the stations that will be sending data.
An example is provided in ``examples/config/station_list.csv``.
Update the file with your stations.

.. code-block:: bash

   cp examples/config/station_list.csv $WIS2BOX_HOST_DATADIR/station_list.csv


Discovery metadata
------------------

Discovery metadata is central to wis2box, wis2box-api, and wis2box-ui.
An example is provided in ``examples/config/surface-weather-observations.yml``.

.. code-block:: bash

   cp examples/config/surface-weather-observations.yml $WIS2BOX_HOST_DATADIR/surface-weather-observations.yml

Edit the file ``$WIS2BOX_HOST_DATADIR/surface-weather-observations.yml`` to provide the correct metadata for your dataset:

* replace ``[iso3c_country].[center_id].data.core.weather.surface-based-observations.SYNOP`` with the topic you used in ``$WIS2BOX_HOST_DATADIR/data-mappings.yml`` previously
* text provided in title and abstract will be displayed in wis2box-ui
* provide a valid bounding-box in bbox

Build wis2box
-------------

Run the ``build`` and ``update`` commands to set up wis2box.
This will start the process of building the wis2box containers from source.

.. code-block:: bash

   python3 wis2box-ctl.py build
   python3 wis2box-ctl.py update

This might take a while the first time.

Start wis2box
-------------

Start wis2box containers and check that all services are running (and healthy).

.. code-block:: bash

   python3 wis2box-ctl.py start
   python3 wis2box-ctl.py status

If neccessary repeat the command until all services are up and running.

Runtime configuration
---------------------

The last design-time steps required to run wis2box are once wis2box is running.

Login to the wis2box container

.. code-block:: bash

   python3 wis2box-ctl.py login

.. note::

   $WIS2BOX_DATADIR is the location that $WIS2BOX_HOST_DATADIR binds to the container.
   This allows wis2box command to access the configuration files from inside the wis2box container.

Setup observation data processing and API publication:

.. code-block:: bash

   wis2box data add-collection $WIS2BOX_DATADIR/surface-weather-observations.yml

Cache and publish station collection and discovery metadata to the API:

.. code-block:: bash

   wis2box metadata discovery publish $WIS2BOX_DATADIR/surface-weather-observations.yml
   wis2box metadata station sync $WIS2BOX_DATADIR/station_list.csv

Logout of wis2box container:

.. code-block:: bash

   exit

Data ingest
-----------

The runtime component of wis2box is data ingestion.
This is an event driven workflow driven by s3 notifications from uploading data to wis2box-storage.
An example is provided in examples/scripts/copy_to_incoming.py.
To access the storage component, visit http://localhost:9001 in your web browser.
The default username/password is minio/minio123

Debugging
---------

Something's now working?
wis2box includes a local grafana-instance to help you collect and view logs and figure out what's wrong.
Visit http://localhost:3000 in your local web browser to view the local grafana instance.

wis2box-ui
----------

wis2box includes a UI to view the data that has been ingested.
To explore, visit http://localhost:8999 in your web browser.

Not seeing data?
After data has been ingested for a station for the first time, you need to re-publish the stations.
This will republish the station with a link relation to any associated observation collection.

.. code-block:: bash

   python3 wis2box-ctl.py execute wis2box metadata station publish-collection
