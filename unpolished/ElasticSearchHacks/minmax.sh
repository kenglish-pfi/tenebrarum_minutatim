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

curl -XPOST "http://$HOST:$PORT/shiavo/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "max_" : { 
            "max" : { "field" : "'$1'" } }, 
        "min_" : { 
            "min" : { "field" : "'$1'" } } 
    } 
}'
