import sys, math, numpy, random, os, traceback

QUARTER_EARTH_CIRCUMFRENCE = 10018750  # in meters

def A(a):
    return numpy.array(a)

e = 1.0/math.sqrt(2.0)
# Second basis is the first basis rotated 45 degrees on all axes so all endpoints are between all endpoints of first basis
# Second basis is not currently used.
basi = [
    A([ A([0,0,0]), A([1,0,0]), A([0,1,0]), A([0,0,1]), A([-1,0,0]), A([0,-1,0]), A([0,0,-1]) ]), 
    A([ A([0,0,0]), A([(e*e),(e*e),(-e)]),  A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]), 
                   -A([(e*e),(e*e),(-e)]),  -A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), -A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]) ])
]

#  Matrix type must be returned so that later code gets expected behavior from built-in operations.
def decomp_vector_from_angle_x(theta):
    C = numpy.matrix([1.0, math.cos(theta)/e, math.sin(theta)/e]) / math.sqrt(3)
    D = C + A([0.7071067811865475244008443621048, 0.0, 0.0])
    D = D / numpy.linalg.norm(D)
    return D

def decomp_vector_from_angle_x(theta):
    X = numpy.matrix([math.sqrt(3)/2.0, math.cos(theta)/2.0, math.sin(theta)/2.0])
    return X

# Six evenly spaced angles
decomposition_angles = [0.0, math.pi/3.0, 2.0*math.pi/3.0, math.pi, 4.0*math.pi/3.0, 5.0*math.pi/3.0]
# Six evenly spaced vectors about the x-axis
decomposition_vectors_about_x_axis = map(decomp_vector_from_angle, decomposition_angles)

def degrees_to_radians(angle):
    rad = math.pi * angle / 180.0
    return rad
    
def radians_to_degrees(rad):
    deg = 180.0 * rad / math.pi
    return deg

def xyz2latlon(xyz):
    lon = numpy.arctan2(xyz[1], xyz[0])
    lat = numpy.arcsin(xyz[2])
    return [lat, lon]

def xyz2latlon_deg(xyz):
    latlon = xyz2latlon(xyz)
    lat_deg = radians_to_degrees(latlon[0])
    lon_deg = radians_to_degrees(latlon[1])
    return [lat_deg, lon_deg]
    
def latlon2xyz(latlon):
    xyz = [math.cos(latlon[0]) * math.cos(latlon[1]), math.cos(latlon[0]) * math.sin(latlon[1]), math.sin(latlon[0])]
    return xyz
    
def latlon_deg2xyz(latlon_deg):
    xyz = latlon2xyz([degrees_to_radians(latlon_deg[0]), degrees_to_radians(latlon_deg[1])])
    return xyz

def level_from_meters(meters):
    dist = QUARTER_EARTH_CIRCUMFRENCE
    level = 0
    while dist > meters:
        dist = dist / 2.0
        level = level + 1
    return level
    
def level_to_meters(level):
    return QUARTER_EARTH_CIRCUMFRENCE / math.pow(2.0, level)
    
def level_to_radians(level):
    return math.pi / math.pow(2.0, level + 2)
        
 
def skew_symetric_cross(v):
    return numpy.matrix( [ [0, -v[2], v[1]] , [v[2], 0, -v[0]] , [-v[1], v[0], 0] ])

# http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
def rot_x_matrix(current_vector):
    V = numpy.cross(current_vector, basi[0][1])
    s = numpy.linalg.norm(V)
    c = numpy.inner(current_vector, basi[0][1])
    if s < 0.00000000000000000001:
        # These responses assume basi[0][1] == [ 1.0,  0.0,  0.0]
        if c < 0:
            return numpy.matrix([[ -1.0,  0.0,  0.0], [ 0.0,  1.0,  0.0], [ 0.0,  0.0,  1.0]])
        else:
            return numpy.matrix([[ 1.0,  0.0,  0.0], [ 0.0,  1.0,  0.0], [ 0.0,  0.0,  1.0]])
    Vx = skew_symetric_cross(V)
    R = Vx + numpy.identity(3) + (numpy.dot(Vx, Vx) * ((1 - c) / (s * s)))
    return R

# Generate one of six evenly spaced vectors oriented in a circle on the unit sphere about current_vector    
#     To make the math "obvious" we compute the new vector about the X axis and then use a
#     rotation matrix to orient this vector about current_vector
#
#     TODO:  Optimize end of this routine:
#     The approach of iteratively sub-dividing the result vector towards the current_vector
#     gives the correct result.  I am sure there is a more direct approach which would again
#     be produced by rotating the result vector towards the current_vector in one step.
def decomposition_vector(current_vector, level, letter):   
    idx = ord(letter) - ord('0')
    
    if idx == 0:
        return current_vector
    W = decomposition_vectors_about_x_axis[idx-1]
    
    # Get the rotation matrix
    R = rot_x_matrix(current_vector)
    X = (W * R).A[0]  # 3x3 Matrix * 1x3 Array ==> 1x3 Matrix ... grab the one and only 1-D vector from the 1-D matrix
    #  This next line shouldn't be necessary, but seems to be
    X = X / numpy.linalg.norm(X)
    if level > 1:
        for i in range(level-1):
            X = current_vector + X
            X = X / numpy.linalg.norm(X)  # normalize, not divide by 2.  Divide by 2 gives the middle point on the chord and not on the sphere.
    return X


# Compute arc-distance between two vectors
def distance(Vect, Wect):    
    c = numpy.dot(Vect, Wect)
    if c < -1.0 or 1.0 < c :
        return math.pi
    
    d = numpy.arccos(c)
    return d;

# Converts a single character in a spherical_geohash string to an angle.
# Called recursively to evaluate a spherical_geohash string
def nibble2vect(level, letter, current_vector=numpy.array([0.0,0.0,0.0])):
    idx = ord(letter) - ord('0')
    if level == 0:
        vect = basi[0][idx]
    else:
        vect = decomposition_vector(current_vector, level, letter)
    return vect

# Heart of this geo-hashing code.  Iteratively finds the decomposed vectors that best 
# describe the objective vector.    
def geovecthash8(xyz, level, search_level=0, seed_hashes = []):
    objective = A(xyz)
    letters = ['0', '1', '2', '3', '4', '5', '6']    
    current_vector = A([0,0,0])
    search_dist = level_to_radians(search_level)
    hashes = [""]
    step_start = 0
    step_end = level
    if len(seed_hashes) > 0:
        hashes = seed_hashes
        step_start = len(seed_hashes)
        step_end = level - step_start + 1
    
    for step in range(step_start, step_end):
        letter_start = 1
        if step > 0:
            letter_start = 0
            
        def possible(letter):
            U = nibble2vect(step, letter, current_vector)  # use same function for forward and reverse encoding for consistent results
            dist = distance(objective, U)
            return (dist, letter, U)
            
        possibles = map(possible, letters[letter_start:])
        possibles.sort()
        
        # check to see if search_level criteria are matched by other options
        if search_level != 0 and step <= search_level:
            for tup in possibles[1:]:
                if tup[0] < search_dist + possibles[0][0]:
                    if step < search_level -1:
                        hashes = hashes + geovecthash8(xyz, search_level, search_level, [hashes[0] + tup[1]])
                    else:
                        hashes.append(hashes[0] + tup[1])
            
        # we will continue to drill into the best (minimal) path
        (min_dist, next_hash_letter, current_vector) = possibles[0]
        hashes[0] = hashes[0] + next_hash_letter
        
    return hashes

   
def geohash(lat_deg, lon_deg, level, search_level=0):
    xyz = latlon_deg2xyz([lat_deg, lon_deg])
    return geovecthash8(xyz, level, search_level)

def geovect(hash):
    current_vector=numpy.array([0.0,0.0,0.0])
    for i in range(len(hash)):
        letter = hash[i:i+1]
        current_vector = nibble2vect(i, letter, current_vector)
    return current_vector

def latlon(hash):
    vector = geovect(hash)
    ll = xyz2latlon_deg(vector)
    return ll
    
    
# Austin :      ['412504100002014005[0]', '52504100002014005[000]']
# print geohash8(-0.1165684, -0.8572452, 0.501540, 0.001)

# San Antonio : ['412504100000004[00000]', '52504100000004[000000]']
# print geohash8(-0.128860005, -0.862881594, 0.488789934, 0.001)

# Edge condition
#  Two points within 8 km of each other but:
#  ['1', '2113636363636363636']
#  versus
#  ['1', '1122626262626262626']
# print geohash8(e - .0001, e + .0001, 0, 0.001)
# print geohash8(e + .0001, e - .0001, 0, 0.001)

def randomTest():
    tests = []
    for i in range(1000):
        lat = 179.0 * (random.random() - 0.50)
        lon = 358.0 * (random.random() - 0.50)
        h = geohash(lat, lon, 8, 4)
        Va = latlon_deg2xyz([lat, lon])
        Vz = geovect(h[0])
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
        hs = geovecthash8(xyz, 3)
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
                print '\t'.join(map(str, geovect(a + b + c)))

def reverseDistances():
    hh = {}
    letters = ['0', '1', '2', '3', '4', '5', '6']
    for a in letters[1:]:
        for b in letters:
            for c in letters:
                hh[a + b + c] = [geovect(a + b + c), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                
    for h0 in hh:
        dists = []
        u = hh[h0][0]
        for h1 in hh:
            if h0 != h1:
                v = hh[h1][0]
                dists.append(distance(u, v))
        dists.sort()
        for i in range(6):
            hh[h0][i+1] = dists[i]
        print '\t'.join(map(str, hh[h0]))

                
# Close vectors to test with for multiple return case:
#
#    geohash(82.9727289148       , -102.972692119, 8)        => 30041310
#    geohash(82.9727289148 + 0.01, -102.972692119 - 0.01, 8) => 30004030
# 
