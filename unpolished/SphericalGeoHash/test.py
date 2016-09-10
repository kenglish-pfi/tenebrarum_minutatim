import sys, math, numpy, random, os, traceback

import algorithm, latlon, util

def randomTest():
    tests = []
    for i in range(1000):
        lat = 179.0 * (random.random() - 0.50)
        lon = 358.0 * (random.random() - 0.50)
        h = geohash(lat, lon, 8, 4)
        Va = latlon_deg2xyz([lat, lon])
        Vz = algorithm.vector(h[0])
        tests.append( (distance(Va, Vz), lat, lon, h) )
        if len(h) > 1:
            print >> sys.stderr, "geohash(" + str(lat) + ", " + str(lon) + ", 8, 4) = " + repr(h)
            
    tests.sort(reverse=True)
    # print the 10 best and worst fits
    for i in range(10):
        print repr(tests[i])
    print " :"
    print " :"
    for i in range(10):
        print repr(tests[-i])

def bucketDistributionTest():
    buckets = {}
    for i in range(6*7*7*300):
        xyz = A([random.random() - 0.50, random.random() - 0.50, random.random() - 0.50])
        xyz = xyz / numpy.linalg.norm(xyz)
        hs = algorithm.hash(xyz, 3)
        bucket = hs[0]
        if bucket not in buckets:
            buckets[bucket] = 0
        buckets[bucket] = buckets[bucket] + 1

    for bucket in buckets:
        print '\t'.join([ bucket, str(buckets[bucket]) ])
#

def reverseDistribution():
    letters = ['0', '1', '2', '3', '4', '5', '6']
    for a in letters[1:]:
        for b in letters:
            for c in letters:
                print '\t'.join(map(str, algorithm.vector(a + b + c)))

# Identify non-peers that are closer than peers:
def closeNonPeers():
    check_d = 1.01 * algorithm.distance(algorithm.vector('100'), algorithm.vector('101'))
    hh = {}
    letters = ['0', '1', '2', '3', '4', '5', '6']
    for a0 in letters[1:]:
        for b0 in letters:
            for a1 in letters[1:]:
                if a1 < a0:
                    continue
                for b1 in letters:
                    if a1+b1 < a0+b0:
                        continue
                    if a0+b0 != a1+b1:
                        for c0 in letters:
                            for c1 in letters:
                                if a1+b1+c1 < a0+b0+c0:
                                    continue
                                d = algorithm.distance(algorithm.vector(a0+b0+c0), algorithm.vector(a1+b1+c1))
                                if  d < check_d:
                                    print '\t'.join([ a0+b0+c0, a1+b1+c1, str(d) ])
                
                
# Check consistency of 'peer' distances at level 3:
def peerDistances():
    letters = ['0', '1', '2', '3', '4', '5', '6']
    for a in letters[1:]:
        for b in letters:
            for c in letters:
                print '\t'.join([ a+b+'0', a+b+c, repr(distance(vector(a+b+'0'), vector(a+b+c))) ])
                

        
# Close vectors to test with for multiple return case:
#
#    geohash(82.9727289148       , -102.972692119, 8)        => 30041310
#    geohash(82.9727289148 + 0.01, -102.972692119 - 0.01, 8) => 30004030
# 
closeNonPeers()