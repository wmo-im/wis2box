.. _quickstart:

Quickstart
==========

Download wis2box and start using Malawi test data:

.. code-block:: bash

    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


For the purposes of a quickstart, this deployment expects the test environment, which includes data and metadata, and runs on localhost. This
is done by using the test environment file:

.. code-block:: bash

    cp tests/test.env dev.env
    vi dev.env


.. note::

    For more information on deployment, see :ref:`administration` and :ref:`configuration`

Start wis2box with Docker Compose and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py status --all # The --all flag shows all containers, even ones that are down.
    python3 wis2box-ctl.py login


Once logged in, verify the enviroment:

.. code-block:: bash

    wis2box environment show


Setup observation data processing and API publication:

.. code-block:: bash

    wis2box api add-collection --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed $WIS2BOX_DATADIR/metadata/discovery/mw-surface-weather-observations.yml


Cache and publish station collection and discovery metadata to the API:

.. code-block:: bash

    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/mw-surface-weather-observations.yml
    wis2box metadata station sync $WIS2BOX_DATADIR/metadata/station/station_list.csv

Ingest and publish data, using data ingest command to update the wis2box-incoming bucket :

.. code-block:: bash

    wis2box data ingest --topic-hierarchy data.core.observations-surface-land.mw-FWCL.landFixed --path $WIS2BOX_DATADIR/observations

Re-publish the stations collection to additionally include link relations to collections with observations published from that station:

.. code-block:: bash

    wis2box metadata station publish-collection

Logout of wis2box container:

.. code-block:: bash

    exit


From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running.

To explore your wis2box installation and services, visit http://localhost:8999 in your web browser.
