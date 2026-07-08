#!/bin/bash

set -e

PROJECT_DIR="/home/pi/roboband"

clear

echo "=========================================="
echo "      RoboBand Installer v1.0"
echo "=========================================="
echo
echo "Select device:"
echo
echo "1) Controller"
echo "2) Robot"
echo "3) Conveyor"
echo

read -rp "Choice [1-3]: " CHOICE

case "$CHOICE" in
    1)
        DEVICE="controller"
        DEFAULT_HOSTNAME="controller"
        INSTALL_BROKER=true
        ;;
    2)
        DEVICE="robot"
        DEFAULT_HOSTNAME="robot"
        INSTALL_BROKER=false
        ;;
    3)
        DEVICE="conveyor"
        DEFAULT_HOSTNAME="conveyor"
        INSTALL_BROKER=false
        ;;
    *)
        echo "Invalid selection."
        exit 1
        ;;
esac

echo
echo "Updating package lists..."
apt update

echo
echo "Installing packages..."

apt install -y \
    python3-paho-mqtt \
    mosquitto-clients \
    avahi-daemon

if [ "$INSTALL_BROKER" = true ]; then

    apt install -y mosquitto

fi

CURRENT_HOSTNAME=$(hostname)

echo
echo "Current hostname: $CURRENT_HOSTNAME"
read -rp "Set hostname to \"$DEFAULT_HOSTNAME\"? [Y/n] " ANSWER

if [[ ! "$ANSWER" =~ ^[Nn]$ ]]; then

    hostnamectl set-hostname "$DEFAULT_HOSTNAME"

    sed -i "s/^127.0.1.1.*/127.0.1.1\t$DEFAULT_HOSTNAME/" /etc/hosts

    HOSTNAME="$DEFAULT_HOSTNAME"

else

    HOSTNAME="$CURRENT_HOSTNAME"

fi

systemctl enable avahi-daemon
systemctl restart avahi-daemon

mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/logs"

if [ "$INSTALL_BROKER" = true ]; then

    mkdir -p /etc/mosquitto/conf.d

    cat >/etc/mosquitto/conf.d/roboband.conf <<EOF
listener 1883
allow_anonymous true
EOF

    systemctl enable mosquitto
    systemctl restart mosquitto

    BROKER="localhost"
    FALLBACK=""

else

    echo
    read -rp "Enter Controller IP: " FALLBACK

    BROKER="controller.local"

    echo
    echo "Testing connection..."

    if ping -c 2 "$FALLBACK" >/dev/null 2>&1; then
        echo "Controller reachable."
    else
        echo
        echo "WARNING: Controller is not reachable."
        echo "Configuration will still be created."
    fi

fi

cat >"$PROJECT_DIR/config.ini" <<EOF
[MQTT]
BROKER=$BROKER
BROKER_FALLBACK=$FALLBACK
PORT=1883

[DEVICE]
TYPE=$DEVICE
HOSTNAME=$HOSTNAME
EOF

chown -R pi:pi "$PROJECT_DIR"

echo
echo "=========================================="
echo "Installation completed"
echo "=========================================="
echo

echo "Device      : $DEVICE"
echo "Hostname    : $HOSTNAME"

if [ "$INSTALL_BROKER" = true ]; then

    IP=$(hostname -I | awk '{print $1}')

    echo
    echo "MQTT Broker : controller.local"
    echo "IP Address  : $IP"

else

    echo
    echo "MQTT Broker : controller.local"
    echo "Fallback IP : $FALLBACK"

fi

echo
echo "Configuration:"
echo "$PROJECT_DIR/config.ini"

echo
echo "MQTT Test"

echo
echo "Subscriber:"
echo "mosquitto_sub -t 'roboband/#' -v"

echo
echo "Publisher:"
if [ "$INSTALL_BROKER" = true ]; then
    echo "mosquitto_pub -h localhost -t roboband/test -m hello"
else
    echo "mosquitto_pub -h controller.local -t roboband/test -m hello"
fi

echo
echo "IMPORTANT:"
echo "If the hostname was changed,"
echo "please reboot the Raspberry Pi."

echo
echo "sudo reboot"

echo
echo "=========================================="
