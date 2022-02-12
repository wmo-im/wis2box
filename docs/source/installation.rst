.. _installation:

Installation
============

wis2box is built for easy installation across various operating systems and environments.

Requirements and dependencies
-----------------------------

wis2box requires `Python`_ 3 and `Docker`_ 1.13.

Core dependencies are installed as containers in the Docker Compose deployment of wis2box. This
is true for the software wis2box itself, which runs as a container orchestrating the necessary
data management workflows of a node as part of the WIS 2.0 network.

Once Python and Docker are installed, wis2box needs to be installed.

ZIP Archive
-----------

.. code-block:: bash

    # curl, wget or download from your web browser
    curl https://github.com/wmo-im/wis2box/archive/refs/heads/main.zip
    cd wis2box-main

GitHub
------

.. code-block:: bash

    # clone wis2box GitHub repository
    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


Summary
-------

Congratulations! Whichever of the abovementioned methods you chose, you have successfully installed wis2box
onto your system. From here, you can get started with test data by following the :ref:`quickstart`, or continue on to
:ref:`configuration`.

.. _`Python`: https://www.python.org/downloads
.. _`Docker`: https://docs.docker.com/get-docker
