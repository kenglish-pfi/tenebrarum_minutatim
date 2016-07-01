# This filter-script just deletes the 2nd and 2nd-to-last lines of the
# output from 
#    curl -XGET "http://$HOST:9200/$INDEX/_settings,_mapping/?pretty"  
# which creates a file that can be passed to 
#    curl -XPOST "http://$HOST:9200/$INDEX -d @$INDEX.create_index.json
import sys

lines = sys.stdin.readlines()
del lines[1]
del lines[-2]
print ''.join( lines )


