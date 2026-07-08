#!/bin/bash

set -e

PROJECT_DIR="/home/pi/projects"
REPO_DIR="$PROJECT_DIR/roboband"
REPO_URL="https://github.com/XMstr-hash/roboband.git"

echo "=========================================="
echo " RoboBand Bootstrap"
echo "=========================================="

echo
echo "Installing required packages..."

sudo apt update
sudo apt install -y git

echo
echo "Creating project directory..."

mkdir -p "$PROJECT_DIR"

if [ -d "$REPO_DIR/.git" ]; then

    echo
    echo "Updating existing repository..."

    cd "$REPO_DIR"
    git pull

else

    echo
    echo "Cloning repository..."

    cd "$PROJECT_DIR"
    git clone "$REPO_URL"

fi

echo
echo "Starting MQTT installer..."

cd "$REPO_DIR/install"

chmod +x mqtt_install.sh

sudo ./mqtt_install.sh
