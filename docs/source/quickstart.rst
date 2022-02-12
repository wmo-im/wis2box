.. _quickstart:

Quickstart
==========

Download wis2box and start using Malawi test data:

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


For the purposes of a quickstart, this deployment expects the test environment, which includes data and metadata. This
is done by using the test environment file:

.. code-block:: bash

    cp tests/test.env dev.env
    vi dev.env


.. note::

    For more information on deployment, see :ref:`administration` and :ref:`configuration`

Start wis2box with Docker Compose and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login


Once logged in, create the enviroment and verify it is correct:

.. code-block:: bash

    wis2box environment create
    wis2box environment show


Setup observation data processing and API publication:

.. code-block:: bash

    wis2box data setup --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed
    wis2box api add-collection /data/wis2box/data/metadata/discovery/surface-weather-observations.yml --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed


Publish station collection and discovery metadata to the API:

.. code-block:: bash

    wis2box metadata station cache /data/wis2box/data/metadata/station/station_list.csv
    wis2box metadata station publish-collection
    wis2box metadata discovery publish /data/wis2box/data/metadata/discovery/surface-weather-observations.yml


Process data via CLI:

.. code-block:: bash

    wis2box data ingest --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed --path /data/wis2box/data/observations/0-454-2-AWSNAMITAMBO-20210707.csv
    wis2box api add-collection-items --recursive --path /data/wis2box/data/public


Logout of wis2box container:

.. code-block:: bash

    exit

Restart wis2box:

.. code-block:: bash

    python3 wis2box-ctl.py start


From here, you can run ``python3 wis2box-ctl.py`` to confirm that containers are running.

In your web browser you should be able to open http://localhost:8999 as well as
http://localhost:8999/pygeoapi/collections to further explore wis2box.
