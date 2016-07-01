import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
from elasticsearch import Elasticsearch
import json
import collections
import subprocess

p_server = sys.argv[1]
p_index = sys.argv[2]
p_doctype = sys.argv[3]
p_id = int(sys.argv[4])

es = Elasticsearch(p_server, timeout="120")

if p_id == 0:
    scroll = es.search(index=p_index, doc_type=p_doctype, body=u'{"query" : { "match_all" : {} }, "size" : "1000" }', search_type="scan", scroll="10m")
    scrollid = scroll[u'_scroll_id']
else:
    scrollid = sys.argv[5]

response = es.scroll(scroll_id=scrollid, scroll= "10m")
if len(response["hits"]["hits"]) != 0:
    # launch next reader process immediately ...
    print >> sys.stderr, "Received " + str(len(response["hits"]["hits"])) + "hits, launching process for scroll_id=" + response[u'_scroll_id']
    subprocess.Popen(["python", "bulk_dump.py", sys.argv[1], sys.argv[2], sys.argv[3], str(p_id+1), response[u'_scroll_id']])
    f = open("bulk--" + p_server + "--" + p_index + "--" + p_doctype + "--" + format(p_id, '06') + ".dat.json", "w")
    for item in response["hits"]["hits"]:
        op_dict = {
            u"index": {
                u"_index": p_index, 
                u"_type" : p_doctype, 
                u"_id": item[u"_id"]
            }
        }
        json.dump(op_dict, f)
        f.write('\n')
        json.dump(item[u"_source"], f)
        f.write('\n')
    
    f.close()
    

