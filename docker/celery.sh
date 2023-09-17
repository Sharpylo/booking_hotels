#!/bin/bash

if [[ "${1}" == "celery" ]]; then
    echo "Executing Celery Worker Command"
    celery --app=app.tasks.celery:celery worker -c 1 -l INFO
elif [[ "${1}" == "flower" ]]; then
    echo "Executing Flower Command"
    celery --app=app.tasks.celery:celery flower
fi