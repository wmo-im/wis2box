.. _administration:

Administration
==============

wis2box is designed to be built as a network of virtual machines within a virtual network. Once this
is built, users login into the main wis2box machine to setup their workflow and configurations for
data processing and publishing.

The ``wis2box-ctl.py`` utility provides a number of tools for managing the wis2box containers.

The following steps provide an example of container management workflow.

.. code-block:: bash

   # build all images
   python3 wis2box-ctl.py build

   # start system
   python3 wis2box-ctl.py start

   # stop system
   python3 wis2box-ctl.py stop

   # view status of all deployed containers
   python3 wis2box-ctl.py status


.. note::

    Run ``python3 wis2box-ctl.py --help`` for all usage options.


With wis2box now installed and started, it's time to start up the box and login to the wis2box container:

.. code-block:: bash

    python3 wis2box-ctl.py start
    python3 wis2box-ctl.py login

Now that you are logged into the wis2box container, it's now time to manage station metadata, discovery metadata
and data processing pipelines.
