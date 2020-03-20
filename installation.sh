#!/usr/bin/env bash

python3 -m venv env
source env/bin/activate

pip install requirements.txt

sudo apt-get install memcached