.. _quickstart:

Quickstart
==========

Requirements and dependencies
-----------------------------

wis2box requires the following prior to installation:

.. csv-table::
   :header: Requirement,Version
   :align: left

   `Python`_,3.8
   `Docker Engine`_, 20.10.14
   `Docker Compose`_,2.4.1

If these are already installed, you can skip to installing wis2box.

- To install Python, follow `Python installation`_.
- To install Docker, follow `Docker Engine installation`_.
- To install Docker Compose, follow `Compose installation`_.

Successful installation can be confirmed by inspecting the versions on your system.

.. code-block:: bash

    docker version
    docker compose version
    python3 -V

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


wis2box configuration
---------------------

Wis2box will read environment variables from dev.env. A baseline is provided in dev.env.example. Copy dev.env.example to dev.env

.. code-block:: bash

    cp config_examples/dev.env.example dev.env

And update it to suit your needs. *You must replace '/your/data/directory'* with a valid directory or your host.

Wis2box configuration requires a file data-mapping.yml. 

Baselines are provided in config_examples/data-mapping.yml.example-* 

For example for publishing *.bufr4 files with SYNOP data: 
Copy this file in the directory you defined for /your/data/directory/

.. code-bloc:: bash

    cp config_examples/data-mapping.yml.example-synop-bufr /your/data/directory/data-mappings.yml

Edit /your/data/directory/data-mappings.yml and change 'member_code3.center_id.data.core.weather.surface-based-observations.SYNOP' to replace 'member_code3' with your corresponding 3-letter location-code and 'center_id' with the unique ID for your MET-center. 

wis2box needs to have a station_list.csv that contains the stations you will process, an example is provided in config_example/station_list.csv.example
Copy this file in the directory you defined for /your/data/directory/

.. code-bloc:: bash

    cp config_examples/station_list.csv.example /your/data/directory/station_list.csv

And update the file for your stations.

.. note::

    For more information on configuration, see :ref:`configuration`

wis2box start
-------------

Start wis2box with Docker Compose and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py status --all # The --all flag shows all containers, even ones that are down.
    
python3 wis2box-ctl.py login

Once logged in, verify the enviroment:

.. code-block:: bash

    wis2box environment show

setup processing and api publication
------------------------------------

First login

.. code-block:: bash
    python3 wis2box-ctl.py login

Once logged in, verify the enviroment:

.. code-block:: bash

    wis2box environment show

Setup observation data processing and API publication:

* Remember to replace 'member_code3.center_id.data.core.weather.surface-based-observations.SYNOP' with the topic you used in data-mappings.yml previously*

.. code-block:: bash

    wis2box api add-collection --topic-hierarchy member_code3.center_id.data.core.weather.surface-based-observations.SYNOP $WIS2BOX_DATADIR/surface-weather-observations.yml


Cache and publish station collection and discovery metadata to the API:

.. code-block:: bash

    wis2box metadata discovery publish $WIS2BOX_DATADIR/surface-weather-observations.yml
    wis2box metadata station sync $WIS2BOX_DATADIR/station_list.csv

Ingest and publish data, using data ingest command to update the wis2box-incoming bucket :

.. code-block:: bash

    wis2box data ingest --topic-hierarchy member_code3.center_id.data.core.weather.surface-based-observations.SYNOP --path $WIS2BOX_DATADIR/observations

Re-publish the stations collection to additionally include link relations to collections with observations published from that station:

.. code-block:: bash

    wis2box metadata station publish-collection

Logout of wis2box container:

.. code-block:: bash

    exit


From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running.

To explore your wis2box installation and services, visit http://localhost:8999 in your web browser.
