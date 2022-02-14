.. _extending-wis2box:

Extending wis2box
==================

At its core, wis2box is a plugin architecture orchestrating all the required components of a node in
the WIS 2.0 network. Driven by topic hierarchies, wis2box can be used to process and publish any type
of geospatial data beyond the requirements of the WIS 2.0 itself.

In this section we will to explore how wis2box can be extended. wis2box plugin development requires
knowledge of how to program in Python as well as Python's packaging and module system.

Building your own data plugin
-----------------------------

The heart of a wis2box data plugin is driven from the ``wis2box.data.base`` abstract base class (ABC)
located in ``wis2box/data/base.py``. Any wis2box plugin needs to inherit from
``wis2box.data.base.BaseAbstractData``. A minimal example can be found below:

.. code-block:: python

    from datetime import datetime
    from wis2box.data.abse import BaseAbstractData

    class MyCoolData(BaseAbstractData):
        """Observation data"""
        def __init__(self, topic_hierarchy: str) -> None:
            super().__init__(topic_hierarchy)

        def transform(self, input_data: Path) -> bool:
            # transform data
            # populate self.output_data with a dict as per:
            self.output_data [{
                '_meta': {
                    'identifier': 'c123'
                    'data_date': datetime_object
                },
                'bufr4': bytes(12356),
                'geojson': geojson_string
            }]
            return True


The key function that plugin needs to implement is the ``transform`` function. This function
should return a ``True`` or ``False`` of the result of the processing, as well as populate
the ``output_data`` property.

The ``output_data`` property should provide a ``list`` of objects with the following properties:

- ``_meta``: object with identifier and Python `datetime`_ objects based on the observed datetime of the data
- ``<format-extension>``: 1..n properties for each format representation, with the key being the filename
  extension. The value of this property can be a string or bytes, depending on whether the underlying data
  is ASCII or binary, for example

Example plugins
---------------

An example plugin for proof of concept can be found in https://github.com/wmo-cop/wis2box-malawi-observations

.. _`datetime`: https://docs.python.org/3/library/datetime.html
