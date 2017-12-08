#!/bin/bash
source bin/activate
./manage.py collectstatic --noinput
./manage.py runserver 10.0.0.96:8000
