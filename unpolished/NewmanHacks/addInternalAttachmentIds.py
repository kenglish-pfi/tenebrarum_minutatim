import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import sys
from elasticsearch import Elasticsearch
import json
import os.path
import datetime, dateutil.parser


# NOTE: this will be multiplied by the number of shards of the index 
#       so we could have ATTACHMENTS_PER_EMAIL*SHARDS*scrollSize attachments 
#       fully loaded into memory at any given point in time.
scrollSize = 100

# There are way too many "ID" fields in this script ... some definitions:
#    From the customer provided "foo_att_crossref.csv" file:
#        MSGID -- The customer's message ID which is the same as the basename of the filename of the *.eml file that originally contained a given email.
#        ATTACHMENT -- The customer's attachment ID that they want to be associated with our attachment objects
#    From the ElasticSearch doc_type="emails" collection:
#        _id -- a GUID: the unique index ID of the email
#        attachments[ { guid } ] -- the _id of the attachment in the doc_type="attachments" collection
#    Not used in the script, but relevant:
#    From the ElasticSearch doc_type="attachments" collection
#        id -- This ties the attachment to the _id of the email above
#        _id -- a GUID: the unique index ID of the attachment

# key is the tuple: (from_address, date, attachment_filename)
# value is the alternateId
alternateAttachmentIdDict = {}

# key is the tuple: (from_address, date)
# value is the alternateId
alternateEmailIdDict = {}

# The FBI's foo_att_crossref file uses "xyz.zip->foo/bar.jar" to assign
# IDs to the files within container files.  We don't extract the internal
# files from container files so we are just going to assign the IDs
# to the container file.  Note that we can obviously wind up with
# multiple IDs for one file.  Elasticsearch inherently supports this.
def cleanAttachmentFilename(filename):
    if "->" in filename:
        return filename[0:filename.index("->")]
    return filename

# This code is very specific to one customer's weird foo_att_crossref file
# 
def loadAlternateIds(crossrefPath, fileFromDatePath):
    first_lookup = {}

    g = open(fileFromDatePath)
    for line in g:
        line = line.rstrip()
        M = line.split('\t')
        if len(M) == 3:
            (filename, from_address, date_str) = M
            ugly_date = date_str[6:]
            dt = dateutil.parser.parse(ugly_date);
            iso_date =dt.strftime("%Y-%m-%dT%H:%M:%S")
            filename = os.path.basename(filename)
            first_lookup[ filename ] = (from_address[6:], iso_date)
    g.close()
    
    line_num = 0
    f = open(crossrefPath)
    for line in f:
        line_num = line_num + 1
        # Skip header
        if line_num == 1:
            continue
            
        A = line.split('\t')
        if len(A) == 6:
            # These not-so-obvious column names are IBM's choices ... just using what is in the CSV
            # MSGID is the alt_ref_id of the email and can be repeated many times in one CSV file.
            # ATTACHMENT is the alt_ref_id of the attachment
            (MSGID, MSGTYPE, ATTACHMENT, DISPLAY, CASE, ACCOUNT) = A
            emailBaseFilename = MSGID + "E.eml"
            (from_address, date_str) = first_lookup[emailBaseFilename]
            attachmentBaseFilename = cleanAttachmentFilename(DISPLAY)
            email_tup = (from_address, date_str)
            if email_tup not in alternateEmailIdDict:
                alternateEmailIdDict[ email_tup ] = MSGID
                # print >> sys.stderr, repr(email_tup) + " => " + MSGID
            attach_tup = (from_address, date_str, attachmentBaseFilename)
            if attach_tup in alternateAttachmentIdDict:
                print >> sys.stderr, "Unexpected repeat attachment key: "  + repr(attach_tup)
            else:
                alternateAttachmentIdDict[ attach_tup ] = ATTACHMENT
            
    f.close()
#

QUERY = '''{
    "size": ''' + str(scrollSize) + ''', 
    "_source": {
        "include": [
            "senders_line",
            "datetime",
            "attachments.guid",
            "attachments.filename"
        ]
    },
    "query": {
        "match_all": {}
    }
}'
'''

def main(serverName, indexName, crossrefPath, fileFromDatePath):
    loadAlternateIds(crossrefPath, fileFromDatePath)
    
    esScrollMails = Elasticsearch(serverName, timeout=120)
    scroll = esScrollMails.search(index=indexName, doc_type="emails", body=QUERY, search_type="scan", scroll="10m")
    scrollId = scroll[u'_scroll_id']
    
    progress = 0
    processed = 0
    while(True):
        response = esScrollMails.scroll(scroll_id=scrollId, scroll= "10m")
        # Yes, this is the documented way to know when we have no more data to process
        if len(response["hits"]["hits"]) == 0:
            break
        # VERY IMPORTANT: must always use most recently returned scroll_id !
        scrollId = response[u'_scroll_id']
        
        bulk_data = []
        
        for r in response[u'hits'][u'hits']:
            progress = progress + len(response[u'hits'][u'hits'])
            source = r[u"_source"]
            tup = (source["senders_line"][0], source["datetime"])
            # print repr(tup)
            if tup not in alternateEmailIdDict:
                print >> sys.stderr, "Sender+Date not found in alternateEmailIdDict: " + repr(tup)
                continue
                
            op_dict = {
                u"update": {
                    u"_index": indexName, 
                    u"_type" : u"emails", 
                    u"_id": r[u"_id"]
                }
            }
            bulk_data.append(op_dict)
            bulk_data.append( {"doc" : {"alt_ref_id" : alternateEmailIdDict[tup] } } )
            processed = processed + 1
            
            for attachment in source[u"attachments"]:
                tup = (source["senders_line"][0], source["datetime"], attachment[u"filename"])
                # print repr(tup)
                if tup not in alternateAttachmentIdDict:
                    print >> sys.stderr, "Sender+Date+Filename not found in alternateAttachmentIdDict: " + repr(tup)
                    continue
                    
                op_dict = {
                    u"update": {
                        u"_index": indexName, 
                        u"_type" : u"attachments", 
                        u"_id": attachment[u"guid"]
                    }
                }
                bulk_data.append(op_dict)
                bulk_data.append( {"doc" : {"alt_ref_id" : alternateAttachmentIdDict[tup] } } )

        # Each update gets its own connection
        if len(bulk_data) > 0:
            bulk_result = Elasticsearch(serverName).bulk(index=indexName, body=bulk_data, refresh="true")
            # print >> sys.stderr, repr(bulk_result)
        print >> sys.stderr, "Progress: " + str(progress) + ", Processed: " + str(processed)
        
           
 
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage:"
        print "export TZ=UTC"
        print "python    " + sys.argv[0] + " server index-name cross-ref-file file-from-date-file"
    
    serverName = sys.argv[1]
    indexName = sys.argv[2]
    crossrefPath = sys.argv[3]
    fileFromDatePath = sys.argv[4]
    main(serverName, indexName, crossrefPath, fileFromDatePath)
#if

###############################################################################
##  REFERENCES
#   https://www.elastic.co/guide/en/elasticsearch/guide/current/bulk.html
#   https://www.elastic.co/guide/en/elasticsearch/guide/current/partial-updates.html


