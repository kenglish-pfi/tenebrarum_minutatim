#!/bin/bash
# "shiavo" is the index name for the sample data that came with the 
# newman-vm-v2.0.9.box 11 gigabyte download.
#
# The necessary field "original_artifact.filename" has not been added
# at this time, so this should basically run but spew a ton of warnings
# to stderr
export TZ=UTC
export INDEX=shiavo

python addInternalAttachmentIds.py localhost $INDEX baz_att_crossref.tab baz_file_key.tab

# Quick verification:
curl -XPOST "http://localhost:9200/"$INDEX"/emails/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "distinct_id__count" : { "cardinality" : { "field" : "id" } },
        "distinct_alt_ref_id__count" : { "cardinality" : { "field" : "alt_ref_id" } }
    }
}'
curl -XPOST "http://localhost:9200/"$INDEX"/attachments/_search?pretty" -d '{ 
    "size": 0, 
    "aggs" : { 
        "distinct_id__count" : { "cardinality" : { "field" : "_id" } },
        "distinct_alt_ref_id__count" : { "cardinality" : { "field" : "alt_ref_id" } }
    }
}'

