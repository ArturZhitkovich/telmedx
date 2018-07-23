#!/bin/bash
source ../../bin/activate
cd ../tel_static/brunch
sudo brunch build
cd ../../
./manage.py collectstatic --noinput

echo " "
echo "To get the status of the app: sudo supervisorctl status"
echo "To restart the instance: sudo supervisorctl restart telx"

