#!/bin/sh

mosquitto_passwd -b -c /mosquitto/config/password.txt $METPX_SR3_BROKER_USERNAME $METPX_SR3_BROKER_PASSWORD

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
