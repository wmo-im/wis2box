#!/bin/sh

# FIXME: derive credentials from env
mosquitto_passwd -b -c /mosquitto/config/password.txt wis2node wis2node

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
