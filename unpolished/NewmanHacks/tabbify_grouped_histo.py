# Formats an ES date_histogram as tab delimited pairs of key_as_string,doc_count values
#
# See spark_line.sh for a usage example.
#
import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
from elasticsearch import Elasticsearch
import json
import collections

def main(group_name, histogram_name):
    R = json.load(sys.stdin)

    for obj_group in R["aggregations"][group_name]["buckets"]:
        for obj_date in obj_group[histogram_name]["buckets"]:
            print '\t'.join([ obj_group["key"], obj_date["key_as_string"], unicode(obj_date["doc_count"]) ])
        
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print u"Usage: "
        print u"    curl -XGET 'http://localhost:9200/index/doctype/' -d { <ES_QUERY> }' | python " + sys.argv[0] + " 'group_name' 'histogram_name'"
        exit()
        
    main(sys.argv[1], sys.argv[2])
# fi
