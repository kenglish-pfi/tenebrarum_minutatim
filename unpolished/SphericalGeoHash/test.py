import unittest
import sys, math, numpy, random, os, traceback
import algorithm, latlon, util

def angleDifference(a, b):
    d = a - b
    d = ((d + math.pi) % (2.0*math.pi)) - math.pi
    return abs(d)

class HashFromVectTests(unittest.TestCase):
    # Use algorithm's internal statics to forcibly create 6x6 vectors
    # close to the initial decomposition vectors of each axis and
    # assert that the corresponding hash starts with the correct
    # letters
    def test_closeToDecompVector(self):
        for letter0 in ['1', '2', '3', '4', '5', '6']:
            cardinalIdx = ord(letter0) - ord('1')
            cardinalVect = algorithm.CARDINAL_BASIS[cardinalIdx]
            for letter1 in ['1', '2', '3', '4', '5', '6']:
                decompIdx = ord(letter1) - ord('1')
                decompVect = algorithm.DECOMPOSITION_VECTORS[cardinalIdx][decompIdx]
                testVect = 99*decompVect + cardinalVect
                testVect = testVect / numpy.linalg.norm(testVect)
                testHash = algorithm.hash(testVect, 4)
                self.assertEqual(testHash[0][0:2], letter0 + letter1)
    
    # Verify that we get the expected hash for an input of a cardinal vector
    def test_cardinalVectorTest(self):
        for letter0 in ['1', '2', '3', '4', '5', '6']:
            cardinalIdx = ord(letter0) - ord('1')
            cardinalVect = algorithm.CARDINAL_BASIS[cardinalIdx]
            testHash = algorithm.hash(cardinalVect, 4)
            self.assertEqual(testHash[0][0:4], letter0 + "000")


class VectFromHashTests(unittest.TestCase):
    # Verify that the vector returned from hash lookup is correct
    def test_cardinalVectorTest(self):
        for letter0 in ['1', '2', '3', '4', '5', '6']:
            cardinalIdx = ord(letter0) - ord('1')
            cardinalVect = algorithm.CARDINAL_BASIS[cardinalIdx]
            testVector = algorithm.vector(letter0 + "000")
            self.assertTrue(numpy.linalg.norm(testVector - algorithm.CARDINAL_BASIS[cardinalIdx]) < .0001)

    # There are many situations where we expect distances to be the same
    def test_uniformDistanceTest(self):
        expected_distance = algorithm.distance(algorithm.vector('1'), algorithm.vector('11'))
        for letter0 in ['1', '2', '3', '4', '5', '6']:
            for letter1 in ['1', '2', '3', '4', '5', '6']:
                test_distance = algorithm.distance(algorithm.vector(letter0), algorithm.vector(letter0 + letter1))
                self.assertTrue( abs(test_distance - expected_distance) < 0.0000001)
        expected_distance = algorithm.distance(algorithm.vector('11'), algorithm.vector('12'))
        for letter0 in ['1', '2', '3', '4', '5', '6']:
            for letters in [ ('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '1')]:
                test_distance = algorithm.distance(algorithm.vector(letter0 + letters[0]), algorithm.vector(letter0 + letters[1]))
                self.assertTrue( abs(test_distance - expected_distance) < 0.0000001)

                
class ConversionTests(unittest.TestCase):
    def test_angleDiff(self):
        for i in range(21):
            for j in range(21):
                a = (i-10) * math.pi / 10.0
                b = (j-10) * math.pi / 10.0
                d0 = abs(i - j)* math.pi / 10.0
                d = angleDifference(a, b)
                if abs(d - d0) >= 0.000001:
                    print repr( (i, j) ) + " => " + str(d0) + "; " + repr( (a, b) ) + " => " + str(d)
                self.assertTrue(abs(d - d0) < 0.000001)
                
    def test_conversions(self):
        for i in range(21):
            for j in range(21):
                for k in range(21):
                    if (i,j,k) == (10,10,10):
                        continue
                    xyz = [10.0 - i, 10.0 - j, 10.0 - k]
                    xyz = xyz / numpy.linalg.norm(xyz)
                    ll = algorithm.xyz2angles(xyz)
                    xyz2 = algorithm.angles2xyz(ll)
                    d = algorithm.distance(xyz, xyz2)
                    if d >= 0.0000001:
                        print repr(xyz) + " => " + repr(ll) + " => " + repr(xyz2) + "; d=" + str(d)
                    self.assertTrue(d < 0.0000001 )
        
class AngleTests(unittest.TestCase):
    def test_randomAgles(self):
        for i in range(1000):
            ll_in = [ math.pi *(random.random() - 0.50),  math.pi *(random.random() - 0.50) / 2.0 ]
            xyz = algorithm.angles2xyz( ll_in )
            hashes = algorithm.hash(xyz, 24)
            xyz2 = algorithm.vector(hashes[0])
            ll_out = algorithm.xyz2angles( xyz2 )
            xyz3 = algorithm.angles2xyz(ll_out)
            self.assertTrue( algorithm.distance(xyz, xyz3) < .00000315)
            
    def test_randomVectors(self):
        for i in range(1000):
            xyz_in = [ random.random(), random.random(), random.random() ]
            xyz_in = xyz_in / numpy.linalg.norm(xyz_in)
            ll = algorithm.xyz2angles( xyz_in )
            xyz_out = algorithm.angles2xyz( ll )
            self.assertTrue( abs( xyz_in[0] - xyz_out[0] ) < 0.000001)
            self.assertTrue( abs( xyz_in[1] - xyz_out[1] ) < 0.000001)
            self.assertTrue( abs( xyz_in[2] - xyz_out[2] ) < 0.000001)
                
#
#  Additional functions for exploring the result space, collecting stats about 
#  the functions, etc ... NOT Unit Tests

def angleError():
    f = open("angleError.log", "w")
    for level in range(4, 8):
        level_results = []
        for i in range(100):
            # ( -PI/2..+PI/2, -PI..+PI )
            ll_in = [ math.pi *(random.random() - 0.50), 2.0 * math.pi *(random.random() - 0.50) ]
            xyz = algorithm.angles2xyz( ll_in )
            hashes = algorithm.hash(xyz, level)
            xyz2 = algorithm.vector(hashes[0])
            ll_out = algorithm.xyz2angles( xyz2 )
            dist = algorithm.distance(xyz, xyz2)
            level_results.append( ('lat', angleDifference(ll_out[0], ll_in[0]), str(dist), str(ll_in[0]), str(ll_in[1]), hashes[0] ) )
            level_results.append( ('lon', angleDifference(ll_out[1], ll_in[1])*math.cos(ll_in[0]), str(dist), str(ll_in[0]), str(ll_in[1]), hashes[0] ) )
        level_results.sort()
        for tup in level_results:
            print >>f, '\t'.join([ str(level), tup[0], str(tup[1]), tup[2], tup[3], tup[4], tup[5] ])
        
            
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

if __name__ == '__main__':
    unittest.main()
