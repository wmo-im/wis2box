=========================================
WMO INFORMATION SYSTEM (WIS) 2.0 IN A BOX
=========================================

 .. epigraph:: The WIS2-in-a-box project was started in November 2021 to provide a system to share data using the `WIS2 framework <https://community.wmo.int/activity-areas/wis>`_ for members of the World Meteorological Organization (WMO).

The “WIS2-in-a-box” software was developed to enable WMO-members to publish and download data through the WIS2-network. The main features are:

* based on existing open-source software widely used in the operations of some WMO Members.
* allows Members to share data internationally and nationally using message queuing protocols (MQP) and Web services in compliance with WIS2 technical regulations
* provides Web APIs complying with Open Geospatial Consortium (OGC) standards, making access to data extremely easy from all common languages (Python, R, ...) and many open-source and proprietary programs (Excel).

Demonstration instances of WIS2-in-a-box can be viewed at https://demo.wis2box.wis.wmo.int.

User guide
==========

The user guide helps you setup your own WIS2-in-a-box instance.

.. toctree::
   :maxdepth: 1
   :caption: User guide:
   :name: toc

   userguide/introduction
   userguide/gettingstarted
   userguide/wis2box-setup
   userguide/data-ingestion
   userguide/public-services
   userguide/mqtt-configuration
   userguide/download

Reference guide
===============

The reference documentation is more complete and programmatic in nature. It contains a comprehensive set
of information on the WIS2-in-a-box software for easy reference.

.. toctree::
   :maxdepth: 1
   :caption: Reference guide:
   :name: toc

   reference_docs/overview
   reference_docs/how-wis2box-works
   reference_docs/configuration
   reference_docs/administration
   reference_docs/quickstart
   reference_docs/running/index
   reference_docs/storage
   reference_docs/monitoring/index
   reference_docs/services
   reference_docs/auth
   reference_docs/data-access/index
   reference_docs/extending-wis2box
   reference_docs/development

Community
=========

.. toctree::
   :maxdepth: 1
   :caption: Community:
   :name: toc

   community/support
   community/troubleshooting
   community/contributing
   community/license