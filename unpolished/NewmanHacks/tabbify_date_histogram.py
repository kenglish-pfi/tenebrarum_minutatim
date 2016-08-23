# Formats an ES date_histogram as tab delimited pairs of key_as_string,doc_count values
import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
import json
import collections

def main(histogram_name):
    R = json.load(sys.stdin)

    for obj in R["aggregations"][histogram_name]["buckets"]:
        print '\t'.join([ obj["key_as_string"], unicode(obj["doc_count"]) ])
        
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print u"Usage: "
        print u"    curl -XGET 'http://localhost:9200/index/doctype/' -d { <ES_QUERY> }' | python " + sys.argv[0] + " 'histogram_name'"
        exit()
        
    main(sys.argv[1])
# fi
