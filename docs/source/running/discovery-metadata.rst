.. _discovery-metadata:


Discovery metadata
==================

Discovery metadata describes a given dataset or collection. Data being published through a wis2box
requires discovery metadata (describing it) to be created, maintained and published to the wis2box
catalogue API.

wis2box supports managing discovery metadata using the WMO Core Metadata Profile (WCMP) 2.0 standard.

.. note::

   WCMP 2.0 is currently in development as part of WMO activities.


Creating a discovery metadata record in wis2box is as easy as completing a YAML configuration file. wis2box
leverages the `pygeometa`_ project's `metadata control file (MCF)`_ format. Below is an example MCF file.


.. literalinclude:: ../../../tests/data/metadata/discovery/surface-weather-observations.yml
   :language: yaml

.. note::

   There are no conventions to the MCF filename. The filename does not get used/exposed or published.
   It is up to the user to determine the best filename, keeping in mind your wis2box system may manage
   and publish numerous datasets (and MCF files) over time.

.. _`pygeometa`: https://geopython.github.io/pygeometa
.. _`metadata control file (MCF)`: https://geopython.github.io/pygeometa/reference/mcf

Summary
-------

At this point, you have created discovery metadata for your given dataset(s).
