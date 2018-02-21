import sys, os, datetime
from pymongo import MongoClient

min_pipeline = [ { "$sort" : { "_id" :  1 } }, { "$limit" : 1 }, { "$project" : { "_id" : "$_id" } } ]
max_pipeline = [ { "$sort" : { "_id" : -1 } }, { "$limit" : 1 }, { "$project" : { "_id" : "$_id" } } ]

min_pad_str = "0000000000000000"
max_pad_str = "ffffffffffffffff"

NOW = datetime.datetime.now()
DATEFMT = "%Y-%m-%d"

def connect(server, port):
    client = MongoClient(server, port)
    return client
#

# Placeholder for ignored exceptions
def ignore():
   return 0
#

# Decomposes min and max aggregation cursor results from MongoDB
def extractResult(aggCursor):
    id_is_oid = False
    oidstr = ""
    dt_str = ""

    aggResult = list(aggCursor)
    oid = aggResult[0]["_id"]
    oidstr = str(oid)
    t = type(oid)
    if str(t) == "<class 'bson.objectid.ObjectId'>":
        id_is_oid = True
        hexstamp = oidstr[0:8]
        dt_str = ""
        try:
            unix_stamp = int("0x" + hexstamp, 16)
            dt_str = datetime.datetime.fromtimestamp(unix_stamp).strftime(DATEFMT)
        except:
            ignore()
    return oidstr, dt_str, id_is_oid
#

#  Main method for dumping stats
#
#  Mainly concerned with identifying which collections have _ids that are of type 'bson.objectid.ObjectId'
#  so that we can convert these ids into date ranges for incremental dumping purposes
#
def dumpStats(server, port):
    CLIENT = connect(server, port)
    
    for dbname in CLIENT.database_names():
        db = CLIENT[dbname]
        for colxname in db.collection_names():
            rmin = db[colxname].aggregate(min_pipeline)
            min_oid, min_dt, id_is_oid = extractResult(rmin)
            rmax = db[colxname].aggregate(max_pipeline)
            max_oid, max_dt, id_is_oid = extractResult(rmax)
            if id_is_oid:
                print('\t'.join( [ dbname, colxname, str(db[colxname].count()), min_dt, max_dt ] ) )
            else:
                print('\t'.join( [ dbname, colxname, str(db[colxname].count()) ] ) )
#

#
# Runs mongodump with passed in query 
#
def dumpExec(server, port, db, coll, qry, dt_week):
    directory = dt_week.strftime(DATEFMT)
    if not os.path.exists(directory):
        os.mkdir(directory)
    ## >> Into Child Dir
    os.chdir(directory)
    CMD = ' '.join( [ "mongodump", "-h", server + ":" + str(port), "-d", db, "-c", coll, "-q", "'" + qry + "'"] )
    print(CMD)
    sys.stdout.flush()
    os.system(CMD)
    os.chdir("..")
    ## << Out of Child Dir

#
#  Main method for dumping data in weekly chunks
#
#  Generates queries for mongodump with bounds on _ids crafted to constrain dump to a weekly (Monday to Monday) time window
#
def dumpWeeklyData(server, port, db, coll, startDate, endDate):
    dt_start = datetime.datetime.strptime(startDate, DATEFMT)
    dt_end = datetime.datetime.strptime(endDate, DATEFMT)
    
    dd = dt_end - dt_start
    wks = dd.days//7
    for i in range(wks):
        dt_A = dt_start + datetime.timedelta(days = i*7)
        dt_Z = dt_start + datetime.timedelta(days = (i+1)*7)
        startOid = hex(int(dt_A.timestamp()))[2:] + min_pad_str
        endOid = hex(int(dt_Z.timestamp()))[2:] + max_pad_str
        QRY = '''{ "_id" : { $gt : ObjectId("''' + startOid + '''"), $lt : ObjectId("''' + endOid + '''") } }'''
        dumpExec(server, port, db, coll, QRY, dt_A)
#

def priorMonday(dtStr):
    dt = datetime.datetime.strptime(dtStr, DATEFMT)
    # If it is not a Monday, make it a Monday
    if dt.weekday() != 0:
        dt = dt - datetime.timedelta(days=dt.weekday())
    return dt.strftime(DATEFMT)
        
def printUsage():
    print("Usage:")
    print("1. Generate stats of all collections on a server:")
    print("   " + sys.argv[0] + " stats <host> <port>")
    print("2. Dump a weeks data from a specific collection:")
    print("   " + sys.argv[0] + " dump <host> <port> <db> <collection> <startDate> [<endDate>]")
    print("       Where:")
    print("           startDate and endDate are in YYYY-MM-DD format")
    print("           if endDate is not given, the most recent Monday is assumed")
#

# Usual main
#
if __name__ == "__main__":
    if len(sys.argv) < 3:
        printUsage()
        exit()
    else:
        if sys.argv[1] == "stats":
            dumpStats(sys.argv[2], int(sys.argv[3]))
        elif sys.argv[1] == "dump":
            (host, port, db, coll, startDate) = sys.argv[2:7]
            port = int(port)
            startDate = priorMonday(startDate)
            
            endDate = priorMonday(NOW.strftime(DATEFMT))
            if len(sys.argv) == 8:
                endDate = priorMonday(sys.argv[7])
            if startDate == endDate:
                print("Error:  startDate and endDate must be a week apart")
                print("        This code does not support partial weekly dumps, only prior weeks can be dumped")
                exit()
            dumpWeeklyData(host, port, db, coll, startDate, endDate)
        else:
            printUsage()
            exit()
#
