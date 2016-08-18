import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import json
import os.path
import datetime, dateutil.parser
from random import randint

foo_att_xref_path = sys.argv[1]
foo_file_key_path = sys.argv[2]

def muss_up_date(iso_date_str):
    dt = dateutil.parser.parse(iso_date_str)
    offset = randint(-4,4)
    dt_mussed = dt + datetime.timedelta(hours=offset)
    if offset <= 0:
        offset_str = "+0" + str(-offset) + "00"
    else:
        offset_str = "-0" + str(offset) + "00"
    return " ".join([ 
        ["Mon,", "Tue,", "Wed,", "Thu,", "Fri,", "Sat,", "Sun,"][dt.weekday()], 
        str(dt.day),
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month - 1],
        str(dt.year),
        str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)+":"+str(dt.second).zfill(2),
        offset_str ])
        

fkeyf = codecs.open(foo_file_key_path, "w", 'UTF-8')
xreff = codecs.open(foo_att_xref_path, "w", 'UTF-8')
# Customer's foo_att_crossref.csv is TAB delimited and has a header
print >> xreff, u"MSGID\tMSGTYPE\tATTACHMENT\tDISPLAY\tCASE\tACCOUNT"

results = json.load(sys.stdin)

msg_id_counter = 0
attachment_counter = 0
for result in results[u"hits"][u"hits"]:
    source = result[u"_source"]
    msg_id_counter = msg_id_counter + 1
    msg_id = u"1" + unicode(msg_id_counter).zfill(7)
    msg_file_name = msg_id + u"E.eml"
    
    print >> fkeyf, u'\t'.join([ "/media/foo/bar/" + msg_file_name, "From: " + source[u"senders_line"][0], "Date: " + muss_up_date(source[u"datetime"]) ])
    
    for attachment in source[u"attachments"]:
        attachment_counter = attachment_counter + 1
        attachment_id = u"1" + unicode(attachment_counter).zfill(7) + u"A"
        print >> xreff, u'\t'.join([ msg_id, u"E", attachment_id, attachment[u"filename"], "BazCase", source["senders"][0] ])

xreff.close()
fkeyf.close()
#