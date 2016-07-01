#!/bin/bash
if [[ "$2" = "" ]]
then
    PORT=9200
else
    PORT=$2
fi
if [[ "$1" = "" ]]
then
    HOST=localhost
else
    HOST=$1
fi

curl "http://$HOST:$PORT/_cat/indices?v"