#!/bin/bash
set -e

if [[ "$1" = "api" || -z $1 ]];then

    export UWSGI_WORKERS=${UWSGI_WORKERS:=1}
    export UWSGI_THREADS=${UWSGI_THREADS:=1}
    export UWSGI_MAX_REQUESTS=${UWSGI_MAX_REQUESTS:=1000}
    export UWSGI_LISTEN_QUEUE=${UWSGI_LISTEN_QUEUE:=5}
    export UWSGI_HTTP_TIMEOUT=${UWSGI_HTTP_TIMEOUT:=60}

    echo "Start api"
    exec uwsgi --http :5000 --need-app -w main:app --master --workers $UWSGI_WORKERS \
               --threads $UWSGI_THREADS --max-requests $UWSGI_MAX_REQUESTS \
               --listen $UWSGI_LISTEN_QUEUE --http-timeout $UWSGI_HTTP_TIMEOUT

elif [ "$1" = "main" ];then
    
    shift
    echo "Run command : python main.py $@"
    python main.py $@

elif [ "$1" = "celery_worker" ];then

    export CELERY_WORKER_CONCURRENCY=${CELERY_WORKER_CONCURRENCY:=1}
    export CELERY_WORKER_MAX_TASKS=${CELERY_WORKER_MAX_TASKS:=1000}
    export C_FORCE_ROOT="true"

    echo "Start celery worker"
    exec celery worker -A app.cel -c $CELERY_WORKER_CONCURRENCY --loglevel=info --maxtasksperchild=$CELERY_WORKER_MAX_TASKS

elif [ "$1" = "celery_beat" ];then

    export C_FORCE_ROOT="true"

    echo "Start celery beat"
    exec celery beat -A app.cel --loglevel=info

else

    echo "Wrong argument : $1"

fi
