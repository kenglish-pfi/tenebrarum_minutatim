import inspect, os, sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
from elasticsearch import Elasticsearch
import json
import collections
from Geohash import geohash

# from http://stackoverflow.com/questions/3718657/how-to-properly-determine-current-script-directory-in-python
def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)
#

def isDateTime(key):
    if isinstance(key, basestring) and key[4:5] == '-' and key[7:8] == '-' and key[10:11] == 'T' and key[13:14] == ':' and key[16:17] == ':' :
        return True
    return False
#

def format_value(field_name, val):
    if isDateTime(val):
        return val[0:10] + u' ' + val[12:18]
    else:
        return val
#

def print_results(doc_type, query_response):
    for agg in query_response[u'aggregations']:
        if u'doc_count' in query_response[u'aggregations'][agg]:
            print u'\t'.join([ doc_type, agg, u"", u"", unicode(query_response[u'aggregations'][agg][u'doc_count']) ])
        elif u'value' in query_response[u'aggregations'][agg]:
            value = format_value(agg, query_response[u'aggregations'][agg][u'value'])
            print u'\t'.join([ doc_type, agg, u"", u"", unicode(value) ])
        elif u'buckets' in query_response[u'aggregations'][agg]:
            for dict in query_response[u'aggregations'][agg][u'buckets']:
                if u'key_as_string' in dict:
                    idx_str = format_value(agg, dict[u'key_as_string'])
                    print u'\t'.join([ doc_type, agg, u"", idx_str, unicode(dict[u'doc_count']) ])
                else:
                    if agg == u"geo__hash": 
                        lats, lons = geohash.decode(dict[u'key'])
                        print u'\t'.join([ doc_type, agg, u"", unicode(dict[u'key']), unicode(dict[u'doc_count']), u"", lats, lons])
                    else:
                        print u'\t'.join([ doc_type, agg, u"", unicode(dict[u'key']), unicode(dict[u'doc_count']) ])
        else:
            print u'\t'.join([ doc_type, agg, unicode(query_response[u'aggregations'][agg]) ])
#

def get_index_stats(index, server, port):
    queries = {}
    # A dictinary of queries for each doc_type each query being with a bunch of agg ... cardinality pieces
    p = os.path.join(get_script_dir(), "newman_es_stats_query.json")
    with open(p, 'r') as f:
        queries_str = f.read()
        queries = json.loads(queries_str)
    for doc_type in queries:
        es = Elasticsearch(server + ":" + port, timeout=120)
        query = json.dumps(queries[doc_type], ensure_ascii=False)
        query_response = es.search(index=index, doc_type=doc_type, body=query)
        print_results(doc_type, query_response)

        
if __name__ == "__main__":

    import sys
    import codecs
    
    if len(sys.argv) == 1:
        print u"Usage: "
        print u"    python " + sys.argv[0] + " index-name optional-server-name optional-port-number"
        exit()

    servername = "localhost"
    portnumber = 9200
    if len(sys.argv) > 3:
        portnumber = int(sys.argv[3])
    if len(sys.argv) > 2:
        servername = sys.argv[2]
    index = sys.argv[1]
    get_index_stats(index, servername, str(portnumber))
# fi
