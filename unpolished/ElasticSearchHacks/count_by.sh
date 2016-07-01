#!/bin/bash
INDEX=$1
FIELD=$2
if [[ "$3" = "" ]]
then
    HOST=localhost
else
    HOST=$3
fi
if [[ "$4" = "" ]]
then
    PORT=9200
else
    PORT=$4
fi

curl -XPOST "http://$HOST:$PORT/"$INDEX"/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "group_by_field" : { 
            "terms" : { "field" : "'$FIELD'" } }, 
    } 
}'
