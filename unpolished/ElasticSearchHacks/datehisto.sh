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

#   curl -XPOST "http://$HOST:$PORT/shiavo/_search?pretty" -d '{ 
#       "size": 0, 
#       "aggs" : {
#           "articles_over_time" : {
#               "date_histogram" : {
#                   "field" : "first_received",
#                   "interval" : "month",
#                   "min_doc_count" : 1
#               }
#           }
#       }
#   }'

curl -XPOST "http://$HOST:$PORT/shiavo/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : {
        "foo_within_range" : {
            "filter" : {
                "range" : {
                    "first_received" : {
                        "gte" : "2005-02-01", 
                        "lte" : "2005-04-01"
                    }
                }
            }, 
            "aggs" : {
                "bar_over_time" : {
                    "date_histogram" : {
                        "field" : "first_received",
                        "interval" : "day",
                        "min_doc_count" : 1
                    }
                }
            }
        }
    }
}'

