#!/bin/bash
HOST=$1
INDEX=$2

MAX_CHILD_COUNT=12
# NOTE: 
#    MAX_CHILD_COUNT is an attempt at being nice ... it is not a hard limit.
#    Each python process below forks itself as quickly as it can read
#    data from the server so if the file IO is slower than the network
#    IO these can pile up.
#    In my usage to date, I typically had 2 python processes per
#    document type running in parallel.

function child_count {
child_count_PID=$$
child_count_NUM=`ps -eo ppid | grep -w $child_count_PID | wc -w`
echo $(( $child_count_NUM - 1 ))
}

function limit_children {
while [ `eval child_count` -gt $MAX_CHILD_COUNT ]
do
sleep 10
done
}

curl -sS -XGET 'http://'$HOST':9200/'$INDEX'/_settings,_mapping/?pretty' | python settings_mapping__to__create_index.py > create_index--$HOST--$INDEX.idx.json
# The following command will re-create the index on the target host:
#      curl -XPOST http://$TARGETHOST:9200/$INDEX -d @$HOST--$INDEX.create_index.json


for DT in `( curl -sS -XGET "http://$HOST:9200/_mapping" | python doctypes_from_mapping.py $INDEX )`
do
    python bulk_dump.py $HOST $INDEX $DT 0
    # above forks itself for every 1000 document-block read from index so we will 
    # have potentially multiple child processes PER document type ...
    limit_children
done

echo "Multiple python bulk_dump.py processes now running ... waiting for all to finish"
wait
