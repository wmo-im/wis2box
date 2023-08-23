.. _getting-started:

Getting started
===============

wis2box can be run on any Linux instance (bare metal or cloud hosted VM) with Python, Docker and Docker Compose installed. 
The recommended OS is Ubuntu 20.04 LTS.

.. note::

   wis2box may work on other operating systems (for example AlmaLinux), but the officially supported OS is Ubuntu.

System requirements
-------------------

System requirements depend on the amount of data ingested.  We recommend minimum 2 vCPUs with 4GB Memory and 16GB of local storage.

For example, the following Amazon AWS EC2 instance types have been utilized as part of various `wis2box demonstrations <https://demo.wis2box.wis.wmo.int>`_.

* 0 - 2000 observations per day: `t3a.medium` instance:

  * 2 vCPUs, x86_64 architecture, 4GB Memory, up to 5 Gigabit network, 16GB attached storage (~35 USD per month for on-demand Linux based OS)
* 2000 - 10000 observations per day: `t3a.large` instance:

  * 2 vCPUs, x86_64 architecture, 8GB Memory, up to 5 Gigabit network, 24GB attached storage (~70 USD per month for on-demand Linux based OS)

Software dependencies
---------------------

The services in wis2box are provided through a stack of `Docker`_ containers, which are configured using `Docker Compose`_. 

wis2box requires the following prior to installation:

.. csv-table::
   :header: Requirement,Version
   :align: left

   Python,3.8 or higher
   Docker Engine, 20.10.14 or higher
   Docker Compose, 2.0 or higher

The following commands be used to setup the required software on Ubuntu 20.04 LTS:

.. code-block:: bash
    
    sudo mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get -y update
    sudo apt-get install -y docker-ce docker-compose-plugin unzip python3-pip
    sudo pip3 install pip --upgrade
    sudo pip3 install pyopenssl --upgrade
    sudo pip3 install requests==2.26.0 urllib3==1.26.0

The following commands can be used to inspect the available versions of Python, Docker and Docker Compose on your system:

.. code-block:: bash

    docker version
    docker compose version
    python3 -V

Once you have verified these requirements, go to :ref:`setup` for a step-by-step guide to install and configure your wis2box.

.. _`Docker`: https://docs.docker.com/get-started/overview
.. _`Docker Compose`: https://github.com/docker/compose/releases
