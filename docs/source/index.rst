=======
Welcome
=======

WIS2 in a box (wis2box) is a Free and Open Source (FOSS) Reference Implementation of a WMO WIS2 Node. The project provides a plug and play toolset to ingest, process, and publish weather/climate/water data using standards-based approaches in alignment with the WIS2 principles.  wis2box also provides access to all data in the `WIS2 network <https://community.wmo.int/activity-areas/wis>`_.  wis2box is designed to have a low barrier to entry for data providers, providing enabling infrastructure and services for data discovery, access, and visualization.

wis2box enables World Meteorological Organization (WMO) members to publish and download data through the WIS2 network. The main features are:

* WIS2 compliant: easily register your wis2box to WIS2 infrastructure, conformant to WMO data and metadata standards
* WIS2 compliance: enables sharing of data to WIS2 using standards in compliance with WIS2 technical regulations
* event driven or interactive data ingest/process/publishing pipelines
* visualization of stations/data on interactive maps
* discovery metadata management and publishing
* download/access of data from WIS 2 network to your local environment
* standards-based data services and access mechanisms:
* robust and extensible plugin framework. Write your own data processing engines and integrate seamlessly into wis2box!
* Free and Open Source (FOSS)
* containerized: use of Docker, enabling easy deployment to cloud or on-premises infrastructure

wis2box deployments currently sharing data on the WIS2 network can be found at https://demo.wis2box.wis.wmo.int.

User guide
==========

The user guide helps you setup your own wis2box instance.

.. toctree::
   :maxdepth: 1
   :caption: User guide
   :name: toc-user

   user/introduction
   user/getting-started
   user/setup
   user/data-ingest
   user/gts-headers-in-wis2
   user/public-services-setup
   user/downloading-data

Reference guide
===============

The reference documentation is more complete and programmatic in nature.  It contains a comprehensive set
of information on wis2box for easy reference.

.. toctree::
   :maxdepth: 1
   :caption: Reference guide
   :name: toc-reference

   reference/wis2
   reference/how-wis2box-works
   reference/configuration
   reference/administration
   reference/quickstart
   reference/running/index
   reference/storage
   reference/monitoring/index
   reference/services
   reference/auth
   reference/data-access/index
   reference/development
   reference/extending-wis2box

Community
=========

The community documentation provides information on where to find support and how to contribute to wis2box.

.. toctree::
   :maxdepth: 1
   :caption: Community
   :name: toc-community

   community/support
   community/troubleshooting
   community/contributing
   community/license
