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
    from wis2box.data.base import BaseAbstractData

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

Packaging
---------

The next step is assembling your plugin using standard Python packaging. All plugin code and configuration files
should be made part of the package so that it can operate independently when running in wis2box.  For distribution and
installation, you have the following options:

- publish to the `Python Package Index (PyPI)`_ and install in the wis2node container with ``pip3 install wis2box-mypackage``
- ``git clone`` or download your package, and install via ``python3 setup.py install``

See the `Python packaging tutorial`_ or `Cookiecutter PyPackage`_ for guidance and templates/examples.

.. note::

   It is recommended to name your wis2box packages with the convention ``wis2box-MYPLUGIN-NAME``, as well as
   adding the keywords/topics ``wis2box`` and ``plugin`` to help discovery on platforms such as GitHub.


Integration
-----------

Once your package is installed on the wis2box container, the data mappings need to be updated to connect
your plugin to a topic hierarchy.  See :ref:`data-mappings` for more information.


An example plugin for proof of concept can be found in https://github.com/wmo-cop/wis2box-malawi-observations

Example plugins
----------------

The following plugins provide useful examples of wis2box plugins implemented
by downstream applications.

.. csv-table::
   :header: "Plugin(s)", "Organization/Project","Description"
   :align: left

   `wis2box-malawi-observations`_,WMO,plugin for Malawi surface observation data
   `wis2box-pyopencdms-plugin`_,OpenCDMS,plugin for connecting the Open Climate Data Management System to wis2box

.. _`datetime`: https://docs.python.org/3/library/datetime.html
.. _`Python Package Index (PyPI)`: https://pypi.org
.. _`Python packaging tutorial`: https://packaging.python.org/en/latest/tutorials/packaging-projects
.. _`Cookiecutter PyPackage`: https://github.com/audreyfeldroy/cookiecutter-pypackage
.. _`wis2box-malawi-observations`: https://github.com/wmo-cop/wis2box-malawi-observations
.. _`wis2box-pyopencdms-plugin`: https://github.com/opencdms/wis2box-pyopencdms-plugin
