import sys, math, numpy, random, os, traceback

def A(a):
    return numpy.array(a)

e = 1.0/math.sqrt(2.0)
# Second basis is the first basis rotated 45 degrees on all axes so all endpoints are between all endpoints of first basis
basi = [
    A([ A([0,0,0]), A([1,0,0]), A([0,1,0]), A([0,0,1]), A([-1,0,0]), A([0,-1,0]), A([0,0,-1]) ]), 
    A([ A([0,0,0]), A([(e*e),(e*e),(-e)]),  A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]), 
                   -A([(e*e),(e*e),(-e)]),  -A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), -A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]) ])
]

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
    
# we need 6 evenly spaced points on a circle perpendicular to the current vector
# At the first iteration we can imagine a cube inside the sphere constructed such
# that just the points of the corners touch the sphere.  The cube's transecting diagonals
# are then the diameter of the sphere = 2.
# The coordinates of the points for one basis are the points of the other basis.
# Each vector in one base will have four vectors in the other base that are closest
# to it.  
    
def generate_center(current_vector, level, letter):   
    idx = ord(letter) - ord('0')
    angles = [0.0, math.pi/3.0, 2.0*math.pi/3.0, math.pi, 4.0*math.pi/3.0, 5.0*math.pi/3.0]
    
    if idx == 0:
        return current_vector
    theta = angles[idx - 1]
    
    R = rot_x_matrix(current_vector)
    print "R: " + repr(R)
    W = numpy.matrix([1.0, math.cos(theta)/e, math.sin(theta)/e]) / math.sqrt(3) 
    print "W: " + repr(W)
    X = (W * R).A[0]  # 3x3 Matrix * 1x3 Array ==> 1x3 Matrix ... grab the one and only 1-D vector from the 1-D matrix
    print "X: " + repr(X)
    #  This next line shouldn't be necessary, but seems to be
    X = X / numpy.linalg.norm(X)
    if level > 1:
        for i in range(level-1):
            X = current_vector + X
            X = X / numpy.linalg.norm(X)  # normalize, not divide by 2.  Divide by 2 gives the middle point on the chord and not on the sphere.
            print str(i) + "_th X: " + repr(X)
    print "generate_center(" + repr(xyz2latlon_deg(current_vector)) + ", " + str(level) + ", '" + letter + "') => " + repr(xyz2latlon_deg(X))
    return X

# Compute arc-distance between two vectors
def distance(Vect, Wect):    
    c = numpy.dot(Vect, Wect)
    if c < -1.0 or 1.0 < c :
        return math.pi
    
    d = numpy.arccos(c)
    print "distance(" + repr(xyz2latlon_deg(Vect)) + ", " + repr(xyz2latlon_deg(Wect)) + ") => " + str(d)
    return d;
    
def nibble2vect(level, letter, current_vector=numpy.array([0.0,0.0,0.0])):
    idx = ord(letter) - ord('0')
    if level == 0:
        vect = basi[0][idx]
    else:
        vect = generate_center(current_vector, level, letter)
    return vect
    
def refine(objective, epsilon, current_vector=numpy.array([0.0,0.0,0.0]), current_error=math.pi, hash=""):
    level = len(hash)
    if level > 29 :
        print "Failed to converge:"
        print "   refine(" + ", ".join([ repr(objective), str(epsilon), repr(current_vector), str(current_error), hash]) + ")"
        return [hash + "7"]

    letters = ['0', '1', '2', '3', '4', '5', '6']
    min_hash = hash
    min_dist = current_error * 1.0000001  # need to epsilon this up so that the constraint "dist < min_dist" can find next steps pairs that end in [0,0,0]
    
    min_U = A([0,0,0])
    start = 1
    if level > 0:
        start = 0
        min_U = current_vector
        
    for u in letters[start:]:  # Very important to skip current-vector choice the first time
        U = nibble2vect(level, u, current_vector)
        dist = distance(objective, U)
        print "?: " + str(dist) + " < " + str(min_dist) + " ll: " + repr(latlon(hash))
        if dist < min_dist:
            min_dist = dist
            min_hash = hash + u
            min_U = U
    
    if min_dist < epsilon:
        return [min_hash]
            
    print min_hash
    return refine(objective, epsilon, min_U, min_dist, min_hash)
    

def geovecthash8(xyz, level):
    objective = A(xyz)
    epsilon = math.pi/(math.pow(2.0, level))
    hashes = refine(objective, epsilon)
    # pad out to level
    for i in range(len(hashes)):
        if len(hashes[i]) < level:
            hashes[i] = hashes[i] + ('0' * (level - len(hashes[i])))
        elif len(hashes[i]) > level:
            print >> sys.stderr, "Warning, generated hash longer than expected:"
            print >> sys.stderr, "geovecthash8(" + repr(xyz) + ", " + str(level) + ") : " + hashes[i]
            hashes[i] = hashes[i][0:level]
    return hashes

   
def geohash(lat_deg, lon_deg, level):
    xyz = latlon_deg2xyz([lat_deg, lon_deg])
    return geovecthash8(xyz, level)

def latlon(hash):
    current_vector=numpy.array([0.0,0.0,0.0])
    for i in range(len(hash)):
        letter = hash[i:i+1]
        current_vector = nibble2vect(i, letter, current_vector)
    return xyz2latlon_deg(current_vector)
    
    
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
    for i in range(1000):
        lat = 179.0 * (random.random() - 0.50)
        lon = 358.0 * (random.random() - 0.50)
        print >> sys.stderr, "geohash(" + str(lat) + ", " + str(lon) + ", 8)"
        h0 = geohash(lat, lon, 8)[0]
        h1 = geohash(lat + 0.01, lon - 0.01, 8)[0]
        pfx = [ os.path.commonprefix([h0[0], h1[0]]), os.path.commonprefix([h0[1], h1[1]]) ]
        N = max( len(pfx[0]), len(pfx[1]) )
        if N < 6 :
            print [lat, lon]
            print h0
            print h1
            return
            
#print geovecthash8([0.15373484,  0.99290733,  0.01481033], 8)

# generate_center([0.0, 180.0], 1, '1') => [0.0, 54.735610317245346]
generate_center(numpy.array([1.0, 0.0, 0.0]), 1, '1')
generate_center(numpy.array([-1.0, 0.0, 0.0]), 1, '1')

