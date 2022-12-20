.. _data-pipeline-plugins:

Data pipeline plugins
=====================

Driven by topic hierarchies, wis2box is a plugin architecture orchestrating all the
required components of a WIS2 node.  wis2box also provides a data pipeline plugin
architecture which allows for users to define a plugin based on a topic hierarchy to
publish incoming data (see :ref:`data-mappings` for more information).


.. seealso:: :ref:`extending-wis2box`
.. seealso:: :ref:`data-mappings`

Default pipeline plugins
------------------------

wis2box provides a number of data pipeline plugins which users can be used "out of the box".


``wis2box.data.csv2bufr.ObservationDataCSV2BUFR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts CSV observation data into BUFR using ``csv2bufr``.  A csv2bufr template
can be configured to process the data accordingly.  In addition, ``file-pattern`` can be used
to filter on incoming data based on a regular expression.  Consult the csv2bufr documentation
for more information on configuration and templating.

``wis2box.data.bufr4.ObservationDataBUFR2GeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin converts BUFR observation data into GeoJSON using ``bufr2geojson``.  A ``file-pattern``
can be used to filter on incoming data based on a regular expression.  Consult the bufr2geojson documentation
for more information on configuration and templating.


``wis2box.data.geojson.ObservationDataGeoJSON``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This plugin is for the purposes of publishing GeoJSON data to the API.


.. _`csv2bufr`: https://csv2bufr.readthedocs.io
.. _`bufr2geojson`: https://github.com/wmo-im/bufr2geojson
