.. _data-access:

Data access
===========

Overview
--------

This section provides examples of interacting with wis2box data services as described
in :ref:`services` using a number of common tools and software packages.

..
    TODO: Getting data from a different wis2box

API
---

.. toctree::
   :maxdepth: 2

   python-requests
   python-OWSLib
   R
   python-mqp-subscribe


Summary
-------

..
    TODO: Summary


Running These Examples
----------------------

To be able to run these examples, one needs to start up a jupyter notebook environment.
Recpie would be somthing like::

   git clone https://github.com/wmo-im/wis2box
   cd docs/site/data-access
   jupyter notebook --ip=0.0.0.0 --port=8888

When jupyter starts up it may open a browser window for you. If not you would
need to to point a browser at http://localhost:8088 to see the menu of notebooks
available in this directory.


