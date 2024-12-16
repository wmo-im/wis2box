#!/bin/sh

echo "Setting mosquitto authentication"
if [ ! -e "/mosquitto/config/password.txt" ]; then
    echo "Adding wis2box users to mosquitto password file"
    mosquitto_passwd -b -c /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
    mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
else
    echo "Mosquitto password file already exists. Update it if needed"
    mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
    mosquitto_passwd -b /mosquitto/config/password.txt $WIS2BOX_BROKER_USERNAME $WIS2BOX_BROKER_PASSWORD
fi

# add max_queued_messages to mosquitto.conf if not already there
if ! grep -q "max_queued_messages" /mosquitto/config/mosquitto.conf; then
    echo "max_queued_messages $WIS2BOX_BROKER_QUEUE_MAX" >> /mosquitto/config/mosquitto.conf
fi

# prepare the acl.conf file
if [ ! -e "/mosquitto/config/acl.conf" ]; then
    echo "Creating mosquitto acl file"	
    echo "user everyone" >> /mosquitto/config/acl.conf
    echo "topic read origin/#" >> /mosquitto/config/acl.conf
    echo " " >> /mosquitto/config/acl.conf
    echo "user $WIS2BOX_BROKER_USERNAME" >> /mosquitto/config/acl.conf
    echo "topic readwrite origin/#" >> /mosquitto/config/acl.conf
    echo "topic readwrite wis2box/#" >> /mosquitto/config/acl.conf
    echo "topic readwrite data-incoming/#" >> /mosquitto/config/acl.conf
    echo "topic read \$SYS/#" >> /mosquitto/config/acl.conf
else
    echo "Mosquitto acl file already exists. Update it if needed"
    # add user everyone to acl.conf if not already there
    if ! grep -q "user everyone" /mosquitto/config/acl.conf; then
        echo "user everyone" >> /mosquitto/config/acl.conf
        echo "topic read origin/#" >> /mosquitto/config/acl.conf
        echo " " >> /mosquitto/config/acl.conf
    fi
    # add user $WIS2BOX_BROKER_USERNAME to acl.conf if not already there
    if ! grep -q "user $WIS2BOX_BROKER_USERNAME" /mosquitto/config/acl.conf; then
        echo "user $WIS2BOX_BROKER_USERNAME" >> /mosquitto/config/acl.conf
        echo "topic readwrite origin/#" >> /mosquitto/config/acl.conf
        echo "topic readwrite wis2box/#" >> /mosquitto/config/acl.conf
        echo "topic readwrite data-incoming/#" >> /mosquitto/config/acl.conf
        echo "topic read \$SYS/#" >> /mosquitto/config/acl.conf
    fi
fi

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

if [ -f /tmp/wis2box.crt ]; then
    echo "SSL enabled"
    echo "setup /mosquitto/certs"
    mkdir -p /mosquitto/certs
    cp /tmp/wis2box.crt /mosquitto/certs
    cp /tmp/wis2box.key /mosquitto/certs
    chown -R mosquitto:mosquitto /mosquitto/certs
    # add listener 8883 block to mosquitto.conf, if not already there
    if ! grep -q "listener 8883" /mosquitto/config/mosquitto.conf; then
        echo "listener 8883" >> /mosquitto/config/mosquitto.conf
        echo "certfile /mosquitto/certs/wis2box.crt" >> /mosquitto/config/mosquitto.conf
        echo "keyfile /mosquitto/certs/wis2box.key" >> /mosquitto/config/mosquitto.conf
    fi
else
    echo "SSL disabled"
fi

# set permission of acl.conf to 0700
chmod 0700 /mosquitto/config/acl.conf

# set owner of mosquitto config folder to mosquitto
chown -R mosquitto:mosquitto /mosquitto/config

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
