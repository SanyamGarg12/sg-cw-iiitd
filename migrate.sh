#!/bin/bash

echo "deleting migration files..."
rm */migrations/000*.py

echo "making migrations..."
python manage.py makemigrations

echo "migrating..."
python manage.py migrate
