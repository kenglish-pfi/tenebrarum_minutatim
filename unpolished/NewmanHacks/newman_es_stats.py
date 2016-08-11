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

def print_results(doc_type, query_response):
    for agg in query_response[u'aggregations']:
        if u'doc_count' in query_response[u'aggregations'][agg]:
            print u'\t'.join([ u"", u"", u"", doc_type, agg, u"", unicode(query_response[u'aggregations'][agg][u'doc_count']) ])
        elif u'value' in query_response[u'aggregations'][agg]:
            print u'\t'.join([ u"", u"", u"", doc_type, agg, u"", unicode(query_response[u'aggregations'][agg][u'value']) ])
        elif u'buckets' in query_response[u'aggregations'][agg]:
            for dict in query_response[u'aggregations'][agg][u'buckets']:
                if u'key_as_string' in dict:
                    print u'\t'.join([ u"", u"", u"", doc_type, agg, dict[u'key_as_string'], unicode(dict[u'doc_count']) ])
                else:
                    if agg == u"geo__hash": 
                        lats, lons = geohash.decode(dict[u'key'])
                        print u'\t'.join([ u"", u"", u"", doc_type, agg, unicode(dict[u'key']), unicode(dict[u'doc_count']), lats, lons])
                    else:
                        print u'\t'.join([ u"", u"", u"", doc_type, agg, unicode(dict[u'key']), unicode(dict[u'doc_count']) ])
        else:
            print u'\t'.join([ doc_type, agg, unicode(query_response[u'aggregations'][agg]) ])
    
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
