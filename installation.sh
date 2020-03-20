#!/usr/bin/env bash
echo "Setting up virtual environment..."
python3 -m venv env
source env/bin/activate

echo "Installing pip3..."
sudo apt install python3-pip

echo "Installing requirements..."
pip3 install requirements.txt

echo "Installing dependencies..."
sudo apt-get install memcached
sudo apt install libmysqlclient-dev
sudo apt install python3-dev
sudo apt install build-essential
sudo apt install libssl-dev