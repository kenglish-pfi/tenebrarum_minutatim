#!/bin/bash
if [[ "$3" = "" ]]
then
    PORT=9200
else
    PORT=$3
fi
if [[ "$2" = "" ]]
then
    HOST=localhost
else
    HOST=$2
fi

curl -XGET 'http://'$HOST':'$PORT'/'$1'/_mapping/?pretty'