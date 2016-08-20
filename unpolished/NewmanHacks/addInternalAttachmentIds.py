import sys, codecs
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import sys
from elasticsearch import Elasticsearch
import json
import os.path
import datetime, dateutil.parser
import re

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
# This code is copy and pasted from:
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L293  (extract())
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L301  (extract())
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L144  (convert_encoded())
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L93   (clean_string())
#
from email.header import decode_header
def pstExtractFilenameCleanAlgorithm(fileName):
    EXPR_OPTS = { 'fix_utf8' : (r'[^\x00-\x7F]', ' '), 
                  'fix_tab' : (r'\t', ' '), 
                  'fix_newline' : (r'\n', '[:newline:]'), 
                  'fix_cr' : (r'\r', ' '), 
                  'fix_forwardslash' : (r'/','_') 
                  } 
    def nth(arr, i, out_of_range=None):
        if len(arr) > i:
            return arr[i]
        return out_of_range
        
    def clean_string(sz, expr_list): 
        return reduce(lambda x,r: re.sub(nth(r,0),nth(r,1,' '), x), expr_list, sz) 
        
    def convert_encoded(text): 
        try: 
            decoded_header = decode_header(text) 
            return u''.join([ unicode(str, charset or 'utf-8') for str, charset in decoded_header ]) 
        except: 
            return text 

    fileName = convert_encoded(fileName) if fileName else "attach_{}".format(attach_count.next())
    fileName = clean_string(
        fileName,
        [
            EXPR_OPTS['fix_utf8'],
            EXPR_OPTS['fix_forwardslash'],
            (r' ', '_'),
            (r'&', '_')
        ])
    return fileName

# This code is copy and pasted from:
#  https://github.com/Sotera/pst-extraction/blob/master/src/utils/functions.py#L10 (head)
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L99  (dateToUTCstr())
#  https://github.com/Sotera/pst-extraction/blob/master/src/email_extract_json_unicode.py#L224  (extract())
from email.utils import parsedate_tz
def pstExtractEmailDateCleanAlgorithm(mail_date):
    #from utils.functions import head
    def head(arr):
        return arr[0]
    def dateToUTCstr(str_date): 
        # this fails to parse timezones out of formats like 
        # Tue, 17 Jun 2010 08:33:51 EDT 
        # so it will assume the local timezone for those cases 
        try: 
            dt = dateutil.parser.parse(str_date) 
        except: # TypeError: 
            dt= datetime.datetime(*parsedate_tz(str_date)[:6]) 
        if not dt.tzinfo: 
            dt = dt.replace(tzinfo=dateutil.tz.tzutc()) 
        dt_tz = dt.astimezone(dateutil.tz.tzutc()) 
        return dt_tz.strftime('%Y-%m-%dT%H:%M:%S') 
    return dateToUTCstr(head(mail_date)) if mail_date else None
#

def dumpAlternateIds(first_lookup, alternateEmailIdDict, alternateAttachmentIdDict):
    altlogf = codecs.open("alternateIds.log", "w", "utf-8")
    print >> altlogf, "first_lookup = {"
    for filename in first_lookup:
        print >> altlogf, filename + " : " + repr(first_lookup[ filename ]) + ","
    print >> altlogf, "}"
    print >> altlogf, "alternateEmailIdDict = {"
    for email_tup in alternateEmailIdDict:
        print >> altlogf, repr(email_tup) + " : " + alternateEmailIdDict[email_tup] + ","
    print >> altlogf, "}"
    print >> altlogf, "alternateAttachmentIdDict = {"
    for attach_tup in alternateAttachmentIdDict:
        print >> altlogf, repr(attach_tup) + " : " + alternateAttachmentIdDict[attach_tup] + ","
    print >> altlogf, "}"
    altlogf.close()

    
# This code is very specific to one customer's weird foo_att_crossref file
#
#   For the emails, the customer's "product ID" is the same as the *.eml filename
#   except for the suffix "E.eml".
#
#   To make things more complicated, the Ingest process threw away the filenames
#   and we cannot afford to re-ingest so we have hacked a per-file identifier
#   based on the sender line and the date line.
#
#   To make things even more complicated, the ingest process applied multiple
#   transforms to the "sender's line" e.g. the header "From: " and transformed
#   the datetime to ISO format ... (and sometimes failed at this).
#
def loadAlternateIds(crossrefPath, fileFromDatePath):
    first_lookup = {}

    g = codecs.open(fileFromDatePath, "r", "iso-8859-1")
    for line in g:
        line = line.rstrip()
        M = line.split('\t')
        if len(M) == 3:
            (eml_filepath, from_line, date_line) = M
            # Our fileFromDate.tab file contains the full path to
            # the eml file, just the basename is in the customer's 
            eml_filename = os.path.basename(eml_filepath)
            sender_line = from_line[6:]
            if len(date_line) <= 6:
                print >> sys.stderr, "Short date_line: '" + date_line + "'"
                continue
            date_ugly_str = date_line[6:]
            try:
                datetime_str = pstExtractEmailDateCleanAlgorithm( [ date_ugly_str ] )  # (this routine wants an array)
            except:
                print >> sys.stderr, "Exception parsing date: pstExtractEmailDateCleanAlgorithm(['" + date_ugly_str + "'])"
                continue
            if datetime == None:
                print >> sys.stderr, "pstExtractEmailDateCleanAlgorithm(['" + date_ugly_str + "']) FAILED:  returned None"
                continue
            email_tup = (sender_line, datetime_str)
            first_lookup[ eml_filename ] = email_tup
            MSGID = eml_filename[0:-5]
            alternateEmailIdDict[ email_tup ] = MSGID
    g.close()
    
    f = codecs.open(crossrefPath, "r", "iso-8859-1")
    for line in f:
        A = line.split('\t')
        if len(A) == 6:
            # These not-so-obvious column names are customer's choices ... just using what is in the CSV
            # MSGID is the alt_ref_id of the email and can be repeated many times in one CSV file.
            # ATTACHMENT is the alt_ref_id of the attachment, DISPLAY is the name of the attached file
            # and can be nested with "->" if the files are containers (zip, rar, etc)
            (MSGID, MSGTYPE, ATTACHMENT, DISPLAY, CASE, ACCOUNT) = A
            if MSGID == "MSGID":
                # then skip header
                continue
            
            emailBaseFilename = MSGID + "E.eml"            
            if emailBaseFilename not in first_lookup:
                print >> sys.stderr, 'MSGID "' + MSGID + '" referenced in "' + crossrefPath + '" not found as filename ../"' + emailBaseFilename + '" in file "' + fileFromDatePath + '"'
                continue
            (from_address, date_str) = first_lookup[emailBaseFilename]
            # First we prune to just the container zip/rar etc because our Ingest code doesn't peek inside these
            attachmentBaseFilename = cleanAttachmentFilename(DISPLAY)
            # Then we apply the pst_extract transformation so we'll match what is in the inded
            attachmentBaseFilename = pstExtractFilenameCleanAlgorithm(attachmentBaseFilename).lower()

            attach_tup = (from_address, date_str, attachmentBaseFilename)
            if attach_tup in alternateAttachmentIdDict:
                print >> sys.stderr, "Warning: Repeated attachment key: "  + repr(attach_tup)
            else:
                alternateAttachmentIdDict[ attach_tup ] = ATTACHMENT
            
    f.close()
    
    dumpAlternateIds(first_lookup, alternateEmailIdDict, alternateAttachmentIdDict)
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
    
    bulkf = open("bulk_changes.elasticbulk.jsonish", "w")
    
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
            if "senders_line" in source and "datetime" in source and len(source["senders_line"]) > 0:
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
            bulk_result = Elasticsearch(serverName, timeout=60).bulk(index=indexName, body=bulk_data, refresh="true")
            print >> sys.stderr, repr(bulk_result)
            for obj in bulk_data:
                print >> bulkf, json.dumps(obj)
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


