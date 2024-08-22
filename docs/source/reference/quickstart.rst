.. _quickstart:

Quickstart with test data
=========================

The 'quickstart' deploys wis2box with test data and provides a vital reference for wis2box developers to validate their contributions do not break the wis2box core functionality.
It is the minimal runtime configuration profile as used in wis2box GitHub CI/CD: `GitHub Actions`_.

.. note:: wis2box web components are run on port 80 by default.  When using wis2box from source, the default port for web components is 8999, to be used for development.

To download wis2box from source:

.. code-block:: bash

   git clone https://github.com/wmo-im/wis2box.git


The test enviroment file is provided in ``tests/test.env``.

To run with the 'quickstart' configuration, copy this file to ``wis2box.env`` in your working directory:

.. code-block:: bash

    cp tests/test.env wis2box.env


Build and update wis2box:

.. code-block:: bash

    python3 wis2box-ctl.py build
    python3 wis2box-ctl.py update


Start wis2box and login to the wis2box-management container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login

Once logged in, verify the enviroment:

.. code-block:: bash

    wis2box environment show

Publish test datasets:

.. code-block:: bash

    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/mw-surface-weather-observations.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/it-surface-weather-observations.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/dz-surface-weather-observations.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/ro-synoptic-weather-observations.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/cd-surface-weather-observations.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/int-wmo-test-ship-hourly.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/int-wmo-test-drifting-buoys.yml
    wis2box dataset publish $WIS2BOX_DATADIR/metadata/discovery/int-wmo-test-wind-profile.yml

Load initial stations:

.. code-block:: bash

    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/malawi.csv --topic-hierarchy origin/a/wis2/mw-mw_met_centre-test/data/core/weather/surface-based-observations/synop
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/italy.csv --topic-hierarchy origin/a/wis2/it-meteoam/data/core/weather/surface-based-observations/synop
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/algeria.csv --topic-hierarchy origin/a/wis2/dz-meteoalgerie/data/core/weather/surface-based-observations/synop
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/romania.csv --topic-hierarchy origin/a/wis2/ro-rnimh-test/data/core/weather/surface-based-observations/synop
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/congo.csv --topic-hierarchy origin/a/wis2/cg-met/data/core/weather/surface-based-observations/synop
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/wmo-test-ship-hourly.csv --topic-hierarchy origin/a/wis2/int-wmo-test/data/core/weather/surface-based-observations/ship-hourly
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/wmo-test-drifting-buoys.csv --topic-hierarchy origin/a/wis2/int-wmo-test/data/core/ocean/surface-based-observations/drifting-buoys
    wis2box metadata station publish-collection --path /data/wis2box/metadata/station/wmo-test-wind-profile.csv --topic-hierarchy origin/a/wis2/int-wmo-test/data/core/weather/surface-based-observations/wind-profile

Ingest data using the data ingest command to push data to the ``wis2box-incoming`` bucket:

.. code-block:: bash

    wis2box data ingest --metadata-id "urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations" --path $WIS2BOX_DATADIR/observations/malawi
    wis2box data ingest --metadata-id "urn:wmo:md:it-meteoam:surface-weather-observations" --path $WIS2BOX_DATADIR/observations/italy
    wis2box data ingest --metadata-id "urn:wmo:md:dz-meteoalgerie:surface-weather-observations" --path $WIS2BOX_DATADIR/observations/algeria
    wis2box data ingest --metadata-id "urn:wmo:md:ro-rnimh-test:synoptic-weather-observations" --path $WIS2BOX_DATADIR/observations/romania
    wis2box data ingest --metadata-id "urn:wmo:md:cg-met:surface-weather-observations" --path $WIS2BOX_DATADIR/observations/congo
    wis2box data ingest --metadata-id "urn:wmo:md:int-wmo-test:surface-weather-observations:ship-hourly" --path $WIS2BOX_DATADIR/observations/wmo/ship-hourly
    wis2box data ingest --metadata-id "urn:wmo:md:int-wmo-test:surface-weather-observations:drifting-buoys" --path $WIS2BOX_DATADIR/observations/wmo/drifting-buoys
    wis2box data ingest --metadata-id "urn:wmo:md:int-wmo-test:surface-weather-observations:wind-profile" --path $WIS2BOX_DATADIR/observations/wmo/wind-profile

Logout of wis2box-management container:

.. code-block:: bash

    exit

From here, you can run ``python3 wis2box-ctl.py status`` to confirm that containers are running properly.

To explore your wis2box installation and services, visit http://localhost in your web browser.

.. _`GitHub Actions`: https://github.com/wmo-im/wis2box/blob/main/.github/workflows/tests-docker.yml
