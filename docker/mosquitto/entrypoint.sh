#!/bin/sh

mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
