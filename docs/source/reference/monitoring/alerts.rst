.. _alerts:

Alerts
======

Receiving Alerts by Email
^^^^^^^^^^^^^^^^^^^^^^^^^

This guide will walk you through the steps to configure Grafana to send email notifications when an alert is triggered on your dashboard. This process involves modifying configuration files and setting up an SMTP server to handle the outgoing emails.

1. Copy the 'grafana.ini' File from Docker Container
----------------------------------------------------

First, you need to extract the 'grafana.ini' file from your Grafana Docker container to your local system. For example:

.. code-block:: bash

    docker cp grafana:/etc/grafana/grafana.ini /your-local-directory
    
This command copies the 'grafana.ini' from the Docker container to your local machine for editing.

2. Modify the 'grafana.ini' File
--------------------------------

Open the 'grafana.ini' file you just copied in a text editor and locate the [smtp] section. You will need to enable SMTP and configure it to use your email provider's SMTP server. Here’s how you can configure it for an email account:

.. image:: ../../_static/smtp-configuration.png
   :width: 800px
   :alt: smtp configuration
   :align: center

.. note::

   The password used in the 'grafana.ini' SMTP configuration is not your regular email account password. 
   Detailed descriptions are provided at the bottom of this page.

3. Mount grafana.ini to the Grafana Container
---------------------------------------------

You now need to ensure that your modified 'grafana.ini' is used by Grafana inside the Docker container. To do this, update the docker-compose-monitoring.yml file to mount the local grafana.ini file into the container:

.. image:: ../../_static/mount-grafana.ini.png
   :width: 800px
   :alt: mount grafana
   :align: center
   
This line tells Docker to use the local version of 'grafana.ini' when starting the Grafana container.

4. Restart wis2box to Applying Changes
--------------------------------------

For the changes to take effect, restart your wis2box environment:

.. code-block:: bash

    python3 wis2box-ctl.py restart

This command stops and then restarts your containers, ensuring that the new configuration is loaded.

5. Setting Up the Notification Channel in Grafana
-------------------------------------------------

Log in to Grafana with your admin credentials:

(1) Navigate to Alerting -> Notification channels.

(2) Click "Add channel" and choose Email as the notification type.

.. image:: ../../_static/add-channel.png
   :width: 800px
   :alt: add channel
   :align: center

Enter your email address in the appropriate field and save the notification channel.

.. image:: ../../_static/notification-channel-detail.png
   :width: 800px
   :alt: notification channel detail
   :align: center

6. Configuring Alerts in Your Grafana Dashboard
-----------------------------------------------

Now, set up alerts within your Grafana dashboard:

(1) Open the dashboard where you want to add an alert.

(2) Go to the panel where you want to add the alert and click on the Alert tab.

(3) Set your alert conditions, then under Notifications, select the email notification channel you configured earlier.

(4) Click Apply and save the dashboard.

(5) Export and save the updated dashboard JSON to ensure the changes are persistent.

.. image:: ../../_static/add-alert-notification.png
   :width: 800px
   :alt: add alert notification
   :align: center

7. Final Step: Testing the Setup
--------------------------------

After setting everything up, trigger an alert in your Grafana dashboard to test if the email notifications are working. You should receive an email when the alert conditions are met.

.. image:: ../../_static/receive-alert-email.png
   :width: 800px
   :alt: receive alert email
   :align: center

.. note::

    The most challenging part of this setup is obtaining the correct SMTP password. Here’s how to do it for different email providers:

    For Gmail:

    (1) Enable Less Secure Apps: If you don't use 2FA, enable "Less secure app access" in your Google account settings.
    (2) Generate an App Password: If you use 2FA:
    (3) Go to your Google Account -> Security -> App passwords.
    (4) Generate a new app password for "Mail".
    (5) Use this app password in the grafana.ini password field.

    For WMO Email or Other Providers:

    (1) Check Provider Documentation: Different providers have different methods for generating app passwords or enabling SMTP.
    (2) Contact IT Support: If you're using a corporate email (like WMO email), contact your IT department to get the correct SMTP settings and password.

