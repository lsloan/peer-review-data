#!/bin/bash

if [ -n "${DOCKER_COMPOSE}" ]; then
    echo 'Checking for DB…'
    while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
        echo 'Waiting for DB…'
        sleep 1 # 1 second
    done
    echo 'DB ready.'

    echo 'Creating migrations for model changes…'
    python manage.py makemigrations peer_review_data
fi

echo 'Running migrations…'
python manage.py migrate

echo 'Running main application…'
python manage.py run

# for debugging purposes, keep container running after job completes
sleep 14400 # 4 hours
