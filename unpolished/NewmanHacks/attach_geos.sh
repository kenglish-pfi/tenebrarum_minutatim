#!/bin/bash
IDX=$1

curl -XPOST "http://localhost:9200/"$IDX"/emails/_search?pretty" -d '{
    "size": 10, 
    "filter" : {
        "exists" : {
            "field" : "attachments.exif.gps.latref"
        }
    },
    "_source": {
        "include": [
            "senders",
            "datetime",
            "attachments.guid",
            "attachments.filename",
            "attachments.exif.gps.coord.lat",
            "attachments.exif.gps.coord.lon"
        ]
    }
}' | python tabbify_geo_attach.py 
