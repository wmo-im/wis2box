.. _quickstart:

Quickstart
==========

Download wis2node and start wis2node using Malawi test data.   

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2node.git
    cd wis2node


For the purposes of a quickstart, this deployment expects the test environment, which includes data and metadata. This is done by using the test environment file.

.. code-block:: bash

    cp tests/test.env dev.env
    vi dev.env

.. note::

    For deployment of wis2node otherwise, edit the local environment variables according to your needs and see Deployment

Start wis2node with Docker Compose and login to the wis2node container

.. code-block:: bash

    python3 wis2node-ctl.py start
    python3 wis2node-ctl.py login


Inside create the enviroment inside docker and ensure it is correct. 

.. code-block:: bash

    wis2node environment create
    wis2node environment show

Setup observation data processing and api publication.

.. code-block:: bash

    wis2node data setup --topic-hierarchy observations-surface-land.mw.FWCL.landFixed
    wis2node api add-collection /data/wis2node/data/metadata/discovery/surface-weather-observations.yml --topic-hierarchy observations-surface-land.mw.FWCL.landFixed

Publish metadata discovery and generate station collection.

.. code-block:: bash

    wis2node metadata discovery publish /data/wis2node/data/metadata/discovery/surface-weather-observations.yml 
    wis2node metadata station cache /data/wis2node/data/metadata/station/station_list.csv
    wis2node metadata station generate-collection

Process data via CLI

.. code-block:: bash

    wis2node data ingest -th observations-surface-land.mw.FWCL.landFixed -p /data/wis2node/data/observations/0-454-2-AWSNAMITAMBO-20210707.csv
    wis2node api add-collections-items -r -p /data/wis2node/data/public
    
Log out of wis2node container

.. code-block:: bash

    exit

Restart wis2node

.. code-block:: bash

    python3 wis2node-ctl.py start


From here you can run python3 wis2node-ctl.py status to confirm containers are running. 
In browser you should be able to open http://localhost:8999 as well as 
http://localhost:8999/pygeoapi/collections to further explore wis2node.
