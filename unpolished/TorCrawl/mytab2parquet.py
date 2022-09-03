import sys
from pyspark import SparkContext
#from pyspark.sql import SQLContext
from pyspark.sql import HiveContext
from pyspark.sql.types import *

def getlines(f):
    buf = f.read()
    lines = buf.split('\002')
    sys.stderr.write('\n=====================================================\nlines: ' + str(len(lines)) + '\n')
    for line in lines:
        yield line


sqlContext = HiveContext(spark.sparkContext)


schema = StructType([
            StructField("code", StringType(), True),
            StructField("url", StringType(), True),
            StructField("response", StringType(), True)])


def checkSplit(line):
    A = line.split('\001')
    if len(A) > 3:
        sys.stderr.write("Multiple parts in line:\n")
        sys.stderr.write(line)
        sys.stderr.write('\n')
        return [ A[0], A[1], '\001'.join(A[2:])]
    elif len(A) < 3:
        return ['','','']
    return A


with open("torcrawl-results.tab", "r") as f:
    rdd = spark.sparkContext.parallelize(getlines(f)).map(checkSplit)
    df = sqlContext.createDataFrame(rdd, schema)
    df.write.parquet('torcrawl-results8.parquet')
