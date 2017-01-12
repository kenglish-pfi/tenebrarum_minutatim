import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
from elasticsearch import Elasticsearch
import json
import collections
import subprocess
import gzip

p_server = sys.argv[1]
p_index = sys.argv[2]
p_doctype = sys.argv[3]
p_partnum = int(sys.argv[4])

es = Elasticsearch(p_server, timeout=120)

if p_partnum == 0:
    body=u'{"query" : { "match_all" : {} }, "size" : "1000" }'
    scroll = es.search(index=p_index, doc_type=p_doctype, body=body, scroll='10m', size=1000)
    scrollid = scroll[u'_scroll_id']
else:
    scrollid = sys.argv[5]

response = es.scroll(scroll_id=scrollid, scroll="10m")
scrollid = response[u'_scroll_id']
if len(response["hits"]["hits"]) != 0:
    # launch next reader process immediately ...
    print >> sys.stderr, "Received " + str(len(response["hits"]["hits"])) + "hits, launching process for scroll_id=" + response[u'_scroll_id']
    subprocess.Popen(["python", "bulk_dump_zip.py", sys.argv[1], sys.argv[2], sys.argv[3], str(p_partnum+1), response[u'_scroll_id']])
    f = gzip.open("bulk--" + p_server + "--" + p_index + "--" + p_doctype + "--" + format(p_partnum, '06') + ".dat.json.gz", "wb")
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
    

