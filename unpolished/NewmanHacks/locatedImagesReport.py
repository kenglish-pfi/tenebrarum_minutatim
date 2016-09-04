import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
import json
import collections

report_items = []

def imageUrl(index_name, i):
    return u'http://localhost:8787/email/attachment?data_set_id=' + index_name + '&attachment_guid=' + report_items[i][3]
    
def emailIndexUrl(index_name, i):
    return u'http://localhost:9200/' + index_name + u'/emails/' + report_items[i][2]

def attachIndexUrl(index_name, i):
    return u'http://localhost:9200/' + index_name + u'/attachments/' + report_items[i][3]
    
def imageId(i):
    return u'img_' + str(i)

def imageName(i):
    return report_items[i][4]

def imageDescription(i):
    return u'File ' + report_items[i][4] + u', sent by: ' + report_items[i][0] + u', on: ' + report_items[i][1]
    
def imageLocation(i):
    return u'lan,lon: (' + unicode(report_items[i][5]) + u', ' + unicode(report_items[i][6]) + u')'
    
def generateReport(index_name):
    print >> sys.stdout, '''<html>
<body>
<table border="1px">
<tr>
<td>
'''
    for i in range(len(report_items)):
        print >> sys.stdout, u'''
<div id="''' + 'div_' + imageId(i) + '''">
    ''' + imageDescription(i) + '''<br />
    Location''' + imageLocation(i) +'''<br />
    Nearest Major City: ''' + '!!! TODO !!!' + '''<br />
    <a href="''' + emailIndexUrl(index_name, i) + '''">Email record</a><br />
    <a href="''' + attachIndexUrl(index_name, i) + '''">Attachment record</a><br />
</div>
</td>
<td>
<img id="''' + 'img_' + imageId(i) + '''" src="''' + imageUrl(index_name, i) + '''" alt="''' + imageName(i) + '''" style="width:200px;height:150px">
</td>
</tr>
'''
    print >> sys.stdout, '''
<table>
</body>
</html>
'''
#
    
def main(index_name):
    R = json.load(sys.stdin)

    for obj in R["hits"]["hits"]:        
        src = obj["_source"]
        for attach in src["attachments"]:
            if "exif" in attach:
                C = [ src["senders"][0], src["datetime"], obj["_id"], attach["guid"], attach["filename"], 
                    attach["exif"]["gps"]["coord"]["lat"], attach["exif"]["gps"]["coord"]["lon"] ]
                report_items.append(C)

    generateReport(index_name)
    
main(sys.argv[1])
