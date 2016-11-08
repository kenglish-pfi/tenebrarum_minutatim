import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import sys
from elasticsearch import Elasticsearch
import json

HOSTS=[ { 'host' : "localhost", 'port' : 9200 } ]
TIMEOUT=120
SCROLL_SIZE = 100

p_index=sys.argv[1]
p_doctype=sys.argv[2]
p_query=sys.argv[3]

es = Elasticsearch( hosts=HOSTS, timeout=TIMEOUT)
scroll = es.search(index=p_index, doc_type=p_doctype, body=p_query, search_type="scan", scroll="10m")
scrollId = scroll[u'_scroll_id']

N = 0
print "["
while(True):
    response = es.scroll(scroll_id=scrollId, scroll= "10m")
    # Yes, this is the documented way to know when we have no more data to process
    if len(response["hits"]["hits"]) == 0:
        break
    
    for hit in response["hits"]["hits"]:
        if N != 0:
            print ","
        print json.dumps(hit)
        N = N + 1
    
    # VERY IMPORTANT: must always use most recently returned scroll_id !
    scrollId = response[u'_scroll_id']
    
print "]"
    
    

