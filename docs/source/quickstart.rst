.. _quickstart:

Quickstart
==========

Requirements and dependencies
-----------------------------

The quickstart assumes wis2box and its dependencies have been installed.
If this is not true, please follow the :ref:`installation` steps first.


Successful installation can be confirmed by inspecting the versions on your system.

.. code-block:: bash

    docker version
    docker-compose version
    python3 -V

The quickstart deploys wis2box with test data.
It is the minimal runtime configuration profile - as used in wis2box Github CI/CD.

.. note::

    For information on how to quickly get started with your own data out of the box, proceed to :ref:`running`.
    For more information on deployment, see :ref:`administration` and :ref:`configuration`.

wis2box passes environment variables from dev.env to its container on startup.
The test enviroment file is provided in ``tests/test.env``.
Copy this file to ``dev.env`` in your working directory.

.. code-block:: bash

    cp tests/test.env dev.env


Build and update wis2box

.. code-block:: bash

    python3 wis2box-ctl.py build
    python3 wis2box-ctl.py update


Start wis2box and login to the wis2box container

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login

Once logged in, verify the enviroment

.. code-block:: bash

    wis2box environment show

Publish test discovery metadata

.. code-block:: bash

    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/mwi-surface-weather-observations.yml
    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/ita-surface-weather-observations.yml
    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/dza-surface-weather-observations.yml


Setup observation collections from discovery metadata

.. code-block:: bash

    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/mwi-surface-weather-observations.yml
    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/ita-surface-weather-observations.yml
    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/dza-surface-weather-observations.yml

Ingest data, using data ingest command to push the wis2box-incoming bucket

.. code-block:: bash

    wis2box data ingest --topic-hierarchy mwi.mwi_met_centre.data.core.weather.surface-based-observations.SYNOP --path $WIS2BOX_DATADIR/observations/malawi
    wis2box data ingest --topic-hierarchy ita.roma_met_centre.data.core.weather.surface-based-observations.SYNOP --path $WIS2BOX_DATADIR/observations/italy
    wis2box data ingest --topic-hierarchy dza.alger_met_centre.data.core.weather.surface-based-observations.SYNOP --path $WIS2BOX_DATADIR/observations/algeria


Cache and publish stations

.. code-block:: bash

    wis2box metadata station sync $WIS2BOX_DATADIR/metadata/station/station_list.csv

Logout of wis2box container:

.. code-block:: bash

    exit

From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running.

To explore your wis2box installation and services, visit http://localhost:8999 in your web browser.
