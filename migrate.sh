#!/bin/bash

echo "deleting migration files..."
rm */migrations/00*.py

echo "making migrations..."
python manage.py makemigrations

echo "migrating..."
python manage.py migrate
