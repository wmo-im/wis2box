.. _quickstart:

Quickstart with test data
=========================

The 'quickstart' deploys wis2box with test data and provides a vital reference for wis2box developers to validate their contributions do not break the wis2box core functionality.
It is the minimal runtime configuration profile as used in wis2box Github CI/CD: `GitHub Actions`_.

The test enviroment file is provided in ``tests/test.env``.

To run with the 'quickstart' configuration, copy this file to ``dev.env`` in your working directory:

.. code-block:: bash

    cp tests/test.env dev.env


Build and update wis2box:

.. code-block:: bash

    python3 wis2box-ctl.py build
    python3 wis2box-ctl.py update


Start wis2box and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login

Once logged in, verify the enviroment:

.. code-block:: bash

    wis2box environment show

Publish test discovery metadata:

.. code-block:: bash

    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/mwi-surface-weather-observations.yml
    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/ita-surface-weather-observations.yml
    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/dza-surface-weather-observations.yml
    wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/rou-synoptic-weather-observations.yml


Setup observation collections from discovery metadata:

.. code-block:: bash

    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/mwi-surface-weather-observations.yml
    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/ita-surface-weather-observations.yml
    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/dza-surface-weather-observations.yml
    wis2box data add-collection $WIS2BOX_DATADIR/metadata/discovery/rou-synoptic-weather-observations.yml

Ingest data using the data ingest command to push data to the ``wis2box-incoming`` bucket:

.. code-block:: bash

    wis2box data ingest --topic-hierarchy mwi.mwi_met_centre.data.core.weather.surface-based-observations.synop --path $WIS2BOX_DATADIR/observations/malawi
    wis2box data ingest --topic-hierarchy ita.roma_met_centre.data.core.weather.surface-based-observations.synop --path $WIS2BOX_DATADIR/observations/italy
    wis2box data ingest --topic-hierarchy dza.alger_met_centre.data.core.weather.surface-based-observations.synop --path $WIS2BOX_DATADIR/observations/algeria
    wis2box data ingest --topic-hierarchy rou.rnimh.data.core.weather.surface-based-observations.synop --path $WIS2BOX_DATADIR/observations/romania


Publish stations:

.. code-block:: bash

    wis2box metadata station publish-collection

Logout of wis2box container:

.. code-block:: bash

    exit

From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running properly.

To explore your wis2box installation and services, visit http://localhost:8999 in your web browser.

.. _`GitHub Actions`: https://github.com/wmo-im/wis2box/blob/main/.github/workflows/tests-docker.yml
