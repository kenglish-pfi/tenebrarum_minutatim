#!/bin/dont-run
#

# you have to do this per-document
curl -XGET 'http://localhost:9200/newman-shiavo/emails/7495b986-22f6-11e6-afc5-080027542fa4/_termvector?pretty=true' -d '{
  "fields" : ["body"],
  "offsets" : false,
  "positions" : false,
  "term_statistics" : true,
  "field_statistics" : false,
  "dfs" : true,
  "filter" : {
      "max_doc_freq" : 20,
      "min_doc_freq" : 3
  }
}'

# Tells you how many distinct terms there are in a given field
curl -XPOST "http://localhost:9200/shiavo/emails/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "distinct_body_terms" : {
            "cardinality" : {
                "field" : "body"
            }
        }
    } 
}'

# Terms that are in at least 3 email bodies and the email document ids containing these terms.
curl -XPOST "http://localhost:9200/newman-shiavo/emails/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "group_by_field" : { 
            "terms" : { 
                "field" : "body",  
                "size" : 10000,
                "min_doc_count": 3,
                "order" : { "_count" : "asc" }
            } ,
            "aggs" : {
                "top_doc_hits" : {
                    "top_hits" : {
                        "sort" : [ ],
                        "size" : 20,
                        "_source" : {
                            "include" : [ "id" ]
                        }
                    }
                }
            }
        }
    } 
}'


# Tells you how many distinct terms there are in a given field
curl -XPOST "http://localhost:9200/shiavo/lda-clustering/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "distinct_idx_count" : {
            "cardinality" : {
                "field" : "idx"
            }
        },
        "distinct_topic_term_count" : {
            "cardinality" : {
                "field" : "topic.term"
            }
        },
        topic_score__min : {
            "min" : {
                "field" : "topic.score"
            }
        },
        topic_score__max : {
            "max" : {
                "field" : "topic.score"
            }
        },
        topic_score__percentiles : {
            "percentiles" : {
                "field" : "topic.score",
                "percents" : [ 20, 40, 80, 90, 100 ]
            }
        }
    } 
}'

curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "distinct_domain_count" : { 
            "cardinality" : {
                "field" : "domain"
            }
        }
    } 
}'


curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "group_by_domain" : { 
            "terms" : { 
                "field" : "domain",  
                "size" : 20,
                "min_doc_count": 2
            } 
        }
    } 
}'

curl -XPOST "http://localhost:9200/shiavo/emails/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "group_by_field" : { 
            "terms" : { 
                "field" : "body",  
                "size" : 20480
            } 
        }
    } 
}' > top_20480_terms.json.log


curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "first_received__min" : {
            "min" : {
                "field" : "first_received"
            }
        },
        "first_sent__min" : {
            "min" : {
                "field" : "first_sent"
            }
        },
        "last_received__min" : {
            "min" : {
                "field" : "last_received"
            }
        },
        "last_sent__min" : {
            "min" : {
                "field" : "last_sent"
            }
        },
        "recepient_datetime__min" : {
            "min" : {
                "field" : "recepient.datetime"
            }
        },
        "sender_datetime__min" : {
            "min" : {
                "field" : "sender.datetime"
            }
        },
        "datetime__min" : {
            "min" : {
                "field" : "datetime"
            }
        },
        
        "first_received__max" : {
            "max" : {
                "field" : "first_received"
            }
        },
        "first_sent__max" : {
            "max" : {
                "field" : "first_sent"
            }
        },
        "last_received__max" : {
            "max" : {
                "field" : "last_received"
            }
        },
        "last_sent__max" : {
            "max" : {
                "field" : "last_sent"
            }
        },
        "recepient_datetime__max" : {
            "max" : {
                "field" : "recepient.datetime"
            }
        },
        "sender_datetime__max" : {
            "max" : {
                "field" : "sender.datetime"
            }
        },
        "datetime__max" : {
            "max" : {
                "field" : "datetime"
            }
        }
        
    }
}'


curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "first_received__date_histogram" : {
            "date_histogram" : {
                "field" : "first_received",
                "interval" : "month",
                "min_doc_count" : 1
            }
        },
        "first_sent__date_histogram" : {
            "date_histogram" : {
                "field" : "first_sent",
                "interval" : "month",
                "min_doc_count" : 1
            }
        }
    }
}'


curl -XPOST "http://localhost:9200/shiavo/email_address/_search?pretty" -d '{ 
   "size": 0, 
    "aggs" : { 
        "distinct_addr__count" : {
            "cardinality" : {
                "field" : "addr"
            }
        },
        "distinct_community__count" : {
            "cardinality" : {
                "field" : "community"
            }
        },
        "distinct_domain__count" : {
            "cardinality" : {
                "field" : "domain"
            }
        },
        "first_received__date_histogram" : {
            "date_histogram" : {
                "field" : "first_received",
                "interval" : "month",
                "min_doc_count" : 1
            }
        },
        "first_sent__date_histogram" : {
            "date_histogram" : {
                "field" : "first_sent",
                "interval" : "month",
                "min_doc_count" : 1
            }
        },
        "group_by_domain" : { 
            "terms" : { 
                "field" : "domain",  
                "size" : 20
            } 
        },
        "group_by_email_id" : { 
            "terms" : { 
                "field" : "email_id",  
                "size" : 20
            } 
        },
        "sender_attachments__count" : {
            "filter" : {
                "exists" : {
                    "field" : "sender_attachments"
                }
            }
        }
    }
}'

curl -XPOST "http://localhost:9200/shiavo/attachments/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "attachment__count" : { "filter" : { "exists" : { "field": "content_extracted" } } },
        "content_extracted__count" : { "filter" : { "bool" : { "must": [{ "match": { "content_extracted": "t" } } ] } } }
        }
    } 
}'

#### This gives guid and filename lists seperately and uselessly
curl -XPOST "http://localhost:9200/shiavo/emails/_search?pretty" -d '{ 
    "size": 10000, 
    "filter" : { 
        "exists" : { "field" : "attachments.filename"  } 
    },
    "fields" : [ "senders_line", "datetime", "attachments.guid",  "attachments.filename"]
}' > shiavo_from_data_attach.json

curl -XPOST "http://localhost:9200/shiavo/emails/_search?pretty" -d '{
  "size": 10000, 
  "_source": {
    "include": [
      "senders_line",
      "datetime",
      "attachments.guid",
      "attachments.filename"
    ]
  },
  "query": {
    "filtered": {
      "query": {
        "match_all": {}
      },
      "filter": {
        "exists" : { "field" : "attachments.filename"  } 
      }
    }
  }
}' > shiavo_from_data_attach.json

