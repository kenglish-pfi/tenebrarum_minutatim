#!/bin/bash
IDX=$1

curl -XPOST "http://localhost:9200/"$IDX"/emails/_search?pretty" -d '{
    "size": 0, 
    "aggs" : { 
        "sparkline" :  {
            "terms" : { 
                "field" : "senders",  
                "size" : 10000,
                "min_doc_count": 12,
                "order" : { "_count" : "asc" }
            },            
            "aggs" : {
                "dates" : {
                    "date_histogram" : {
                        "field" : "datetime",
                        "interval" : "day",
                        "min_doc_count" : 1
                    }
                }
            }
        }
    }
}' | python tabbify_grouped_histo.py sparkline dates
