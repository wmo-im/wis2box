#!/bin/sh

# derive credentials from WIS2NODE_BROKER
CREDENTIALS=`echo $WIS2NODE_BROKER | awk -F/ '{print $3}' | awk -F@ '{print $1}' | sed 's/:/ /'`

mosquitto_passwd -b -c /mosquitto/config/password.txt $CREDENTIALS

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
