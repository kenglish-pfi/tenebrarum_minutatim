#  This script processes the file allCountries.txt and prints out JSON objects 
#  in mongodb bulk ingest ready format.
#
#  allCountries.txt obtained from:  http://download.geonames.org/export/dump/allCountries.7z
#  also depends on the lookups:
#      http://download.geonames.org/export/dump/admin1CodesASCII.txt
#      http://download.geonames.org/export/dump/admin2Codes.txt
#
#  The lat,lon values are represented in MongoDB prefered format for its GeoIndexes.
#
#  Note that allCountries.txt is scanned 3 times during this process, the first two times
#  are to extract the info for the Admin3 and Admin4 lookups which are circularly refferential
#
import sys, codecs, json
sys.path.append("..")
from Unicode import UnicodeNormalizer

uninorm = UnicodeNormalizer.UnicodeNormalizer()

if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    sys.stdin=open(0, 'r', encoding='utf-8', closefd=False)
    sys.stdout=open(1, 'w', encoding='utf-8', closefd=False)
    sys.stderr=open(2, 'w', encoding='utf-8', closefd=False)
else:
    sys.stdout=codecs.getreader('UTF-8')(sys.stdin)
    sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
    sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
    def print(a):
        sys.stdout.write(a + '\n')


admin1 = {}
admin2 = {}
admin3 = {}
admin4 = {}

empty = []

def safeSplit(val):
    if len(val) > 0:
        return val.split(',')
    return []
    
def lookupAdmin1(country_code, admin1_code):
    k = ".".join( [country_code, admin1_code] )
    if k in admin1:
        return admin1[ k ]
    else:
        return set([])
    
def lookupAdmin2(country_code, admin1_code, admin2_code):
    k = ".".join( [country_code, admin1_code, admin2_code] )
    if k in admin2:
        return admin2[ k ]
    else:
        return set([])
        
def lookupAdmin3(admin3_code):
    if admin3_code in admin3:
        return admin3[admin3_code]
    else:
        return set([])
        
def lookupAdmin4(admin4_code):
    if admin4_code in admin4:
        return admin4[admin4_code]
    else:
        return set([])

def noteAdmin34( geonameid, name, asciiname, alternatenames, latitude, longitude, 
            feature_class, feature_code, country_code, cc2, 
            admin1_code, admin2_code, admin3_code, admin4_code, population, 
            elevation, dem, timezone, modification_date ):
            if len(admin3_code) > 0:
                if admin3_code not in admin3:
                    admin3[admin3_code] = empty
            if len(admin4_code) > 0:
                if admin4_code not in admin4:
                    admin4[admin4_code] = empty
                    
def nameAdmin34( geonameid, name, asciiname, alternatenames, latitude, longitude, 
            feature_class, feature_code, country_code, cc2, 
            admin1_code, admin2_code, admin3_code, admin4_code, population, 
            elevation, dem, timezone, modification_date ):
            
            if geonameid in admin3:
                admin3[geonameid] = set( [ name.casefold(), asciiname.casefold() ] )
            if geonameid in admin4:
                admin4[geonameid] = set( [ name.casefold(), asciiname.casefold() ] )

def xfold(s):
    return uninorm(s)
                
def processLine( geonameid, name, asciiname, alternatenames, latitude, longitude, 
            feature_class, feature_code, country_code, cc2, 
            admin1_code, admin2_code, admin3_code, admin4_code, population, 
            elevation, dem, timezone, modification_date ):
    
    keys = set( [ name.casefold(), asciiname.casefold() ] )
    primary_names = set( keys )
    if len(alternatenames) > 0:
        primary_names |= set(map(xfold, alternatenames.split(',')))
    
    for k in keys:
        obj = { 
            "k": k, 
            "n" : list(primary_names), 
            "c" : country_code, 
            "t" : feature_class, 
            "loc" : { "coordinates" : [latitude, longitude], "type": "Point" },
            "a1" : list(map(xfold, lookupAdmin1(country_code, admin1_code))),
            "a2" : list(map(xfold, lookupAdmin2(country_code, admin1_code, admin2_code))),
            "a3" : list(lookupAdmin3(admin3_code)),
            "a4" : list(lookupAdmin4(admin4_code)),
            "x" : geonameid
        }
        print(json.dumps(obj))
    

with codecs.open("admin1CodesASCII.txt", 'r', 'utf-8') as f:
    for line in f:
        line = line.rstrip()
        A = line.split('\t')
        if len(A) == 4:
            admin1[A[0]] = set( [ A[1].casefold(), A[2].casefold() ] )
        
with codecs.open("admin2Codes.txt", 'r', 'utf-8') as f:
    for line in f:
        line = line.rstrip()
        A = line.split('\t')
        if len(A) == 4:
            admin2[A[0]] = set( [ A[1].casefold(), A[2].casefold() ] )
            
with codecs.open("allCountries.txt", 'r', 'utf-8') as f:
    for line in f:
        line = line.rstrip()
        A = line.split('\t')
        if len(A) == 19:
            noteAdmin34(*A)

with codecs.open("allCountries.txt", 'r', 'utf-8') as f:
    for line in f:
        line = line.rstrip()
        A = line.split('\t')
        if len(A) == 19:
            nameAdmin34(*A)

def main():
    with codecs.open("allCountries.txt", 'r', 'utf-8') as f:
        for line in f:
            line = line.rstrip()
            A = line.split('\t')
            if len(A) == 19:
                processLine(*A)
            
        
main()
