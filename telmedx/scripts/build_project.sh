#!/bin/bash
source ../venv/bin/activate
cd ../tel_static/brunch
sudo brunch build
cd ../../
./manage.py collectstatic --noinput
