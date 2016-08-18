import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
from elasticsearch import Elasticsearch
import json
import collections
import datetime, dateutil.parser


MAX_EMAIL_COUNT = 10000


def date_to_index(start_date_str, date_str):
    dt0 = dateutil.parser.parse(start_date_str)
    # must strip trailing 'Z' to make python date substraction happy
    if date_str[-1:] == 'Z':
        date_str = date_str[0:-1]
    dt = dateutil.parser.parse(date_str)
    if p_interval == 'day':
        return (dt - dt0).days
        
    if p_interval == 'week':
        monday0 = (dt0 - datetime.timedelta(days=dt0.weekday()))
        monday = (dt - datetime.timedelta(days=dt.weekday()))
        return (monday - monday0).days / 7
        
    if p_interval == 'month':
        return (dt.year - dt0.year)*12 + dt.month - dt0.month

def query_from_template(start_date_str, end_date_str, interval, max_email_count):
    return u'''{
    "size": 0, 
    "filter" : {
        "range" : {
            "senders" : {
                "gt" : "''' + start_date_str + '''",
                "lt" : "''' + end_date_str + '''"
            }
        }
    },
    "aggs" : {
        "senders_found" : { 
            "terms" : { 
                "field" : "senders",  "size" : ''' + str(max_email_count) + '''
            } ,
            "aggs" : {
                "dates" : {
                    "date_histogram" : {
                        "field" : "datetime",
                        "interval" : "''' + interval + '''",
                        "min_doc_count" : 1
                    }
                }                
            }
        }
    }
}
'''
#

def extract_timeseries(server, index, doctype, start_date_str, end_date_str, interval, entity_file, data_file):
    entity_file = open(p_entity_file, "w")
    data_file = open(p_data_file, "w")
    bucket_size = date_to_index(start_date_str, end_date_str) + 1
    

    es = Elasticsearch(p_server, timeout=120)

    query = query_from_template(start_date_str, end_date_str, interval, MAX_EMAIL_COUNT)
    
    #body=u'{"query" : ' + query + ', "size" : "' + str(MAX_EMAIL_COUNT) + '" }'
    response = es.search(index=p_index, doc_type=p_doctype, body=query, size=MAX_EMAIL_COUNT)

    for address_obj in response["aggregations"]["senders_found"]["buckets"]:
        address = address_obj["key"]
        print >> entity_file, address
        out_buckets = [0]*bucket_size
        for date_obj in address_obj["dates"]["buckets"]:
            date_str = date_obj["key_as_string"]
            val = date_obj["doc_count"]
            idx = date_to_index(start_date_str, date_str)
            if idx < 0 or idx > bucket_size:
                print >> sys.stderr, "Unexpected date value: " + date_str
            else:
                out_buckets[idx] = val
            
        print >> data_file, ','.join(map(str, out_buckets))

    entity_file.close()
    data_file.close()
#

##################################### MAIN ####################################
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print u"Usage: "
        print u"    python " + sys.argv[0] + " server index doctype start_date_str end_date_str interval entity_file data_file"
        print u"      interval is one of day week month "
        print u"    e.g.:"
        print u"    python " + sys.argv[0] + " localhost shiavo emails 2005-01-01 2005-07-01 week ts_entity.csv ts_data.csv"
        exit()

    p_server = sys.argv[1]
    p_index = sys.argv[2]
    p_doctype = sys.argv[3]
    p_start_date = sys.argv[4]  # e.g. 2005-01-01
    p_end_date = sys.argv[5]    # e.g. 2005-01-01
    p_interval = sys.argv[6]    # day , week , month
    p_entity_file = sys.argv[7]
    p_data_file = sys.argv[8]
    
    extract_timeseries(p_server, p_index, p_doctype, p_start_date, p_end_date, p_interval, p_entity_file, p_data_file)
# fi

###############################################################################
#
#  APPENDIX A -- Query Result Sample
#
QUERY_RESULTS_LOOK_LIKE = '''
{

    "took": 8591,
    "timed_out": false,
    "_shards": {
        "total": 5,
        "successful": 5,
        "failed": 0
    },
    "hits": {
        "total": 0,
        "max_score": 0,
        "hits": [ ]
    },
    "aggregations": {
        "senders_found": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 76487,
            "buckets": [
                {
                    "key": "pklowefamily@yahoo.com",
                    "doc_count": 205,
                    "dates": {
                        "buckets": [
                            {
                                "key_as_string": "2005-03-24T00:00:00.000Z",
                                "key": 1111622400000,
                                "doc_count": 1
                            }
                            ,
                            {
                                "key_as_string": "2005-03-25T00:00:00.000Z",
                                "key": 1111708800000,
                                "doc_count": 204
                            }
                        ]
                    }
                }
                ,
                :
                :
                ,
                {
                    "key": "ndbaxter@swbell.net",
                    "doc_count": 2,
                    "dates": {
                        "buckets": [
                            {
                                "key_as_string": "2005-03-23T00:00:00.000Z",
                                "key": 1111536000000,
                                "doc_count": 1
                            }
                            ,
                            {
                                "key_as_string": "2005-03-25T00:00:00.000Z",
                                "key": 1111708800000,
                                "doc_count": 1
                            }
                        ]
                    }
                }
            ]
        }
    }
}
'''
