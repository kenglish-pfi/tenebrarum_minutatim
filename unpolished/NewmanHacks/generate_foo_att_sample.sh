#!/bin/bash
#  Run this script on the Newman VM
export TZ=UTC

curl -XPOST "http://localhost:9200/shiavo/emails/_search?pretty" -d '{
  "size": 10000, 
  "_source": {
    "include": [
      "senders",
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
}' | python generate_foo_att_sample.py baz_att_crossref.tab baz_file_key.tab



