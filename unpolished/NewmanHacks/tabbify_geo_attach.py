import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
import json
import collections

    
def main():
    R = json.load(sys.stdin)

    for obj in R["hits"]["hits"]:        
        src = obj["_source"]
        for attach in src["attachments"]:
            if "exif" in attach:
                C = [ src["senders"], src["datetime"], attach["guid"], attach["filename"], 
                    attach["exif"]["gps"]["coord"]["lat"], attach["exif"]["gps"]["coord"]["lon"] ]
            else:
                C = [ src["senders"], src["datetime"], attach["guid"], attach["filename"], 
                    "", "" ]
            print u'\t'.join( map(unicode, C) )

main()