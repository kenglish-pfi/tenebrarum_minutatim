# This filter-script converts the output of the command:
#    curl -XGET "http://$HOST:9200/_mapping"
# and turns it into the list of doc_types that are included in the index given by argv[1]
import sys, json

mapping_doc = json.load(sys.stdin)
for doc_type in mapping_doc[sys.argv[1]]["mappings"]:
    print doc_type