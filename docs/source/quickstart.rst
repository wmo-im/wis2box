.. _quickstart:

Quickstart
==========

Download wis2box and start wis2box using Malawi test data.   

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


For the purposes of a quickstart, this deployment expects the test environment, which includes data and metadata. This is done by using the test environment file.

.. code-block:: bash

    cp tests/test.env dev.env
    vi dev.env

.. note::

    For deployment of wis2box otherwise, see :ref:`configuration`

Start wis2box with Docker Compose and login to the wis2box container

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login


Inside create the enviroment inside docker and ensure it is correct. 

.. code-block:: bash

    wis2box environment create
    wis2box environment show

Setup observation data processing and api publication.

.. code-block:: bash

    wis2box data setup --topic-hierarchy observations-surface-land.mw.FWCL.landFixed
    wis2box api add-collection /data/wis2box/data/metadata/discovery/surface-weather-observations.yml --topic-hierarchy observations-surface-land.mw.FWCL.landFixed

Publish metadata discovery and generate station collection.

.. code-block:: bash

    wis2box metadata discovery publish /data/wis2box/data/metadata/discovery/surface-weather-observations.yml 
    wis2box metadata station cache /data/wis2box/data/metadata/station/station_list.csv
    wis2box metadata station generate-collection

Process data via CLI

.. code-block:: bash

    wis2box data ingest -th observations-surface-land.mw.FWCL.landFixed -p /data/wis2box/data/observations/0-454-2-AWSNAMITAMBO-20210707.csv
    wis2box api add-collections-items -r -p /data/wis2box/data/public
    
Log out of wis2box container

.. code-block:: bash

    exit

Restart wis2box

.. code-block:: bash

    python3 wis2box-ctl.py start


From here you can run python3 wis2box-ctl.py status to confirm containers are running. 
In browser you should be able to open http://localhost:8999 as well as 
http://localhost:8999/pygeoapi/collections to further explore wis2box.
