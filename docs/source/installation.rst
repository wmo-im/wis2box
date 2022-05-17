.. _installation:

Installation
============

wis2box leverages `Docker`_ for easy installation across operating systems and environments.

Requirements and dependencies
-----------------------------

Dependencies are installed as containers in the deployment of wis2box. This
is true for the wis2box software itself, which runs as a container orchestrating the necessary
data management workflows of a node in the WIS 2.0 network.

wis2box runs on `Python`_ 3.8, `Docker Engine`_ 20.10.14, and `Docker Compose`_ 2.4.1.
If these are already installed, you can skip to installing wis2box.

    - To install Python, follow `Python installation`_.
    - To install Docker, follow `Docker Engine installation`_.
    - To install Docker Compose, follow `Compose installation`_.

Successful installation can be confirmed by inspecting the versions on your system.

.. code-block:: bash

    docker version
    docker compose version
    python3 -V

.. note::

    Docker may require post-install configuration. Linux users may need to follow `post install`_
    steps to grant docker privileges. Users in corporate settings my need to configure
    Docker's `HTTP/HTTPS proxy`_.


Installing wis2box
------------------

Once Python and Docker are installed, the wis2box software needs to be installed.

ZIP Archive
^^^^^^^^^^^

wis2box can be installed from a ZIP archive of a the latest branch or a `wis2box release`_.

.. code-block:: bash

    # curl, wget or download from your web browser
    curl https://github.com/wmo-im/wis2box/archive/refs/heads/main.zip
    cd wis2box-main

GitHub
^^^^^^

wis2box can also be installed using the git CLI.

.. code-block:: bash

    # clone wis2box GitHub repository
    git clone https://github.com/wmo-im/wis2box.git
    cd wis2box


Summary
-------

Congratulations! Whichever of the abovementioned methods you chose, you have successfully installed wis2box
onto your system. From here, you can get started with test data by following the :ref:`quickstart`, or continue on to
:ref:`configuration`.


.. _`Docker`: https://docs.docker.com/get-started/overview/
.. _`Docker Compose`: https://github.com/docker/compose/releases
.. _`Compose installation`: https://docs.docker.com/compose/install/
.. _`Docker Engine`: https://docs.docker.com/engine/release-notes/
.. _`Docker Engine installation`: https://docs.docker.com/engine/install/
.. _`HTTP/HTTPS proxy`: https://docs.docker.com/config/daemon/systemd/#httphttps-proxy
.. _`post install`: https://docs.docker.com/engine/install/linux-postinstall/
.. _`Python`: https://www.python.org/downloads/release/python-380/
.. _`Python installation`: https://www.python.org/downloads
.. _`wis2box release`: https://github.com/wmo-im/wis2box/releases