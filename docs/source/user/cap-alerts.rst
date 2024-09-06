.. _cap-alerts:

Publishing CAP Alerts to a wis2box
=================

Here we explain how one can use the `CAP Composer <https://github.com/wmo-raf/cap-composer>`_ to automate the publishing of CAP alerts to a wis2box.

Requirements
------------
In addition to a running wis2box, you will need to install, configure, and run the CAP Composer. For information on how to do this, please consult the `CAP Composer documentation <https://nmhs-cms.readthedocs.io/en/stable/_docs/Manage-CAP-Alerts.html>`_.

Process Outline
---------------
For automated publishing of CAP alerts to a wis2box, we will need to perform the following steps:
* Create a dataset in the wis2box to store the CAP alerts.
* Configure your wis2box broker details in the CAP Composer.

Dataset Creation
----------------
Firstly, there must be a dataset in the wis2box for the CAP alerts to be stored. To create a dataset, simply navigate to the 'Dataset Editor' page in the wis2box-webapp, available on your host at `http://<your-public-ip>/wis2box-webapp`. For more information on how to create a dataset, please see the :ref:`adding-datasets` section of the wis2box setup guide.

When creating a new dataset for CAP alerts, ensure that the 'weather/advisories-warnings' template is selected:

.. image:: ../_static/cap/template_selection.png
   :alt: CAP Dataset
   :align: center

To finish.

MQTT configuration
------------------
To finish.

Publishing an Alert
-------------------
To finish.

Verifying Receipt of a Published Alert
--------------------------------------
To finish.
