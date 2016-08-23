curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{
        "size": 0, 
        "aggs" : { 
            "hist" : {
                "date_histogram" : {
                    "field" : "first_received",
                    "interval" : "month",
                    "min_doc_count" : 1
                }
            }
    }
}' | python tabbify_date_histogram.py "hist" 