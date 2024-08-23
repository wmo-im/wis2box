#!/bin/sh

if [ -f /tmp/wis2box.crt ]; then
    echo "SSL enabled"
    echo "setup /mosquitto/certs"
    mkdir -p /mosquitto/certs
    cp /tmp/wis2box.crt /mosquitto/certs
    cp /tmp/wis2box.key /mosquitto/certs
    chown -R mosquitto:mosquitto /mosquitto/certs
    cp -f /mosquitto/config/mosquitto-ssl.conf /mosquitto/config/mosquitto.conf
else
    echo "SSL disabled"
fi

echo "Setting mosquitto authentication"
if [ ! -e "/mosquitto/config/password.txt" ]; then
    echo "Adding wis2box users to mosquitto password file"
    mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
    mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
else
    echo "Mosquitto password file already exists. Skipping wis2box user addition."
fi

sed -i "s#_WIS2BOX_BROKER_QUEUE_MAX#$WIS2BOX_BROKER_QUEUE_MAX#" /mosquitto/config/mosquitto.conf
sed -i "s#_WIS2BOX_BROKER_USERNAME#$WIS2BOX_BROKER_USERNAME#" /mosquitto/config/acl.conf

for i in `env | grep -Ee "\<WIS2BOX_BROKER_USERNAME_[[:alnum:]]+"`; do
    NAME_TAIL=`echo $i | awk -FWIS2BOX_BROKER_USERNAME_ '{print $2}' | awk -F= '{print $1}'`
    username=WIS2BOX_BROKER_USERNAME_$NAME_TAIL
    password=WIS2BOX_BROKER_PASSWORD_$NAME_TAIL
    topic=WIS2BOX_BROKER_TOPIC_$NAME_TAIL
    echo ${!username}, ${!password}
    mosquitto_passwd -b /mosquitto/config/password.txt ${!username} ${!password}
    echo "user ${!username}" >>  /mosquitto/config/acl.conf
    echo "topic readwrite ${!topic}" >>  /mosquitto/config/acl.conf
done

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
