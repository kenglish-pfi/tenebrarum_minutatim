import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import json
import collections
from Geohash import geohash

#   From: http://download.geonames.org/export/dump/
#   The main 'geoname' table has the following fields :
#   ---------------------------------------------------
#   geonameid         : integer id of record in geonames database
#   name              : name of geographical point (utf8) varchar(200)
#   asciiname         : name of geographical point in plain ascii characters, varchar(200)
#   alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
#   latitude          : latitude in decimal degrees (wgs84)
#   longitude         : longitude in decimal degrees (wgs84)
#   feature class     : see http://www.geonames.org/export/codes.html, char(1)
#   feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
#   country code      : ISO-3166 2-letter country code, 2 characters
#   cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
#   admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
#   admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
#   admin3 code       : code for third level administrative division, varchar(20)
#   admin4 code       : code for fourth level administrative division, varchar(20)
#   population        : bigint (8 byte int) 
#   elevation         : in meters, integer
#   dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
#   timezone          : the timezone id (see file timeZone.txt) varchar(40)
#   modification date : date of last modification in yyyy-MM-dd format

def generateAllGeohashes():
    # See https://en.wikipedia.org/wiki/Geohash  for Base-32 letter choices.
    C = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',    'b', 'c', 'd', 'e', 'f', 'g', 'h',    'j', 'k',    'm', 'n',    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z' ]
    return [a+b+c for a in C for b in C for c in C]
            

def generateCityMapping(level):
    ghashes = {}
    f = codecs.open("cities1000.txt", "r", "utf-8")
    h = codecs.open("largestCityPerHash" + str(level) + ".tab", "w", "utf-8")
    for line in f:
        line = line.rstrip()
        A = line.split(u'\t')
        if len(A) == 19:
            (geonameid           ,
                name             ,
                asciiname        , 
                alternatenames   ,
                latitude         , 
                longitude        , 
                feature_class    , 
                feature_code     , 
                country_code     , 
                cc2              , 
                admin1_code      , 
                admin2_code      , 
                admin3_code      , 
                admin4_code      , 
                population       , 
                elevation        , 
                dem              , 
                timezone         , 
                modification_date  ) = A
            if feature_class == 'P':
                gh = geohash.encode(float(latitude), float(longitude), level)
                if gh not in ghashes:
                    ghashes[gh] = []
                ghashes[gh].append( (long(population), name, country_code, admin2_code, admin1_code, latitude, longitude) )

    # print >> sys.stderr, "cities1000.txt processed"
    
    for gh in ghashes:
        if len(ghashes[gh]) > 1:
            ghashes[gh].sort(reverse=True)
            ghashes[gh] = [ ghashes[gh][0] ]
    f.close()
    
    # print >> sys.stderr, "ghashes CAR(sort())"
    
    # Now use airport list to see if we can fill any blanks:
    g = codecs.open("airport-codes.csv", "r", "utf-8")
    # print >> sys.stderr, "airport-codes.csv opened"
    for line in g:
        line = line.rstrip()
        A = line.split(u',')
        # print >> sys.stderr, str(len(A))
        if len(A) == 13:
            if A[0] == u"ident":
                continue
            (ident,type,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,iso_region,municipality,gps_code,iata_code,local_code) = A
            # print >> sys.stderr, iata_code
            gh = geohash.encode(float(latitude_deg), float(longitude_deg), level)
            if gh not in ghashes:
                print >> sys.stderr, "Found airport for location:" + municipality + ", " + iso_country
                if len(municipality) == 0:
                    municipality = name
                ghashes[gh] = [ (0, municipality,  iso_country, name, iata_code, latitude_deg, longitude_deg) ]
    
    g.close()
    
    for gh in ghashes:
        print >> h, u"\t".join([ gh, ghashes[gh][0][1], ghashes[gh][0][2], ghashes[gh][0][3],ghashes[gh][0][4], str(ghashes[gh][0][5]),str(ghashes[gh][0][6]), str(ghashes[gh][0][0]) ])
    
    h.close()
#

majorCityMap={}
def loadMajorCityMap():
    f = codecs.open("largestCityPerHash3.tab", "r", "utf-8")
    for line in f:
        line = line.rstrip()
        A = line.split('\t')
        majorCityMap[A[0]] = A
    f.close()

def closestCity(lat, lon):
    if len(majorCityMap) == 0:
        loadMajorCityMap()
    gh = geohash.encode(lat, lon, 3)
    if gh in majorCityMap:
        (hash, name, country_code, admin2_code, admin1_code, latitude, longitude, population) = majorCityMap[gh]
    else:
        (name, country_code, admin2_code, admin1_code, latitude, longitude) = ("?","?","?","?","?","?")
    return name, country_code, admin2_code, admin1_code, latitude, longitude

# generateCityMapping(3)
# print repr(generateAllGeohashes())

print closestCity(45.27055, 37.38716)
print closestCity(0.0, 0.0)

