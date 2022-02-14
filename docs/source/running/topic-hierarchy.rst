.. _topic-hierarchy:

Topic hierarchy
===============

.. note::

   The WIS 2.0 topic hiearchies are currently in development. wis2box implementation
   of the topic hiearchies will change, based on ratifications/updates of the topic
   hierarchies in WMO technical regulations and publications.

wis2box implements the WIS 2.0 topic hierarchies, which are designed to efficiently
categorize and classify data, by implementing directory hierarchies. For example,
the below exemplifies a WIS 2.0 topic hierarchy as implemented in wis2box:

.. csv-table::
   :header: WIS 2.0 topic hierarchy,wis2box directory
   :align: left

   ``foo.bar.baz``,``foo/bar/baz``

wis2box topic hierarchies are managed **under** the various wis2box directories, and
are used as part of both design time and runtime workflow.

To create a wis2box topic hierarchy:

.. code-block:: bash

   wis2box data setup --topic-hierarchy foo.bar.baz


This will create the topic hierarchy under the required wis2box directories in support
of automated processing and publishing.

To view a given topic hierarchy setup:

.. code-block:: bash

   wis2box data info --topic-hierarchy foo.bar.baz
