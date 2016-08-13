import sys, math, numpy, random, os

def A(a):
    return numpy.array(a)

e = 1.0/math.sqrt(2.0)
# Second basis is the first basis rotated 45 degrees on all axes so all endpoints are between all endpoints of first basis
basi = [
    A([ A([0,0,0]), A([1,0,0]), A([0,1,0]), A([0,0,1]), A([-1,0,0]), A([0,-1,0]), A([0,0,-1]) ]), 
    A([ A([0,0,0]), A([(e*e),(e*e),(-e)]),  A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]), 
                   -A([(e*e),(e*e),(-e)]),  -A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), -A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]) ])
]

def skew_symetric_cross(v):
    return numpy.matrix( [ [0, -v[2], v[1]] , [v[2], 0, -v[0]] , [-v[1], v[0], 0] ])

# http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
def rot_x_matrix(current_vector):
    V = numpy.cross(current_vector, basi[0][1])
    s = numpy.linalg.norm(V)
    if s < 0.00000000000000000001:
        return numpy.identity(3)
    c = numpy.inner(current_vector, basi[0][1])
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
    W = numpy.array([1.0, math.cos(theta)/e, math.sin(theta)/e]) / math.sqrt(3) 
    X = (W * R).A[0]  # 3x3 Matrix * 1x3 Array ==> 1x3 Matrix ... grab the one and only 1-D vector from the 1-D matrix
    print repr(X)
    if level > 1:
        for i in range(level-1):
            X = current_vector + X
            X = X / numpy.linalg.norm(X)  # normalize, not divide by 2.  Divide by 2 gives the middle point on the chord and not on the sphere.
    print repr(X)
    return X

# Compute arc-distance between two vectors
def distance(Vect, Wect):
    c = numpy.dot(Vect, Wect)
    return numpy.arccos(c)
    
def nibble2vect(level, letter, current_vector=numpy.array([0.0,0.0,0.0])):
    idx = ord(letter) - ord('0')
    if level == 0:
        vect = basi[0][idx]
    else:
        vect = generate_center(current_vector, level, letter)
    return vect
    
def refine(objective, epsilon, current_vector=numpy.array([0.0,0.0,0.0]), current_error=2.0, hash=""):
    level = len(hash)
    if level > 29 :
        print "Failed to converge:"
        print "   refine(" + ", ".join([ repr(objective), str(epsilon), repr(current_vector), str(current_error), hash]) + ")"
        return hash + "7"

    letters = ['0', '1', '2', '3', '4', '5', '6']
    min_hash = hash
    min_dist = current_error * 1.0000001  # need to epsilon this up so that the constraint "dist < min_dist" can find next steps pairs that end in [0,0,0]
    
    if level == 0:
        min_U = A([0,0,0])
        for u in letters[1:]:  # Very important to skip zero-vector the first time
            U = nibble2vect(0, u)
            dist = distance(objective, U)
            if dist < min_dist:
                min_dist = dist
                min_hash = hash + u
                min_U = U
                
        current_error = min_dist
        hash = min_hash
        return refine(objective, epsilon, min_U, current_error, hash)
        
    else:
        min_U = current_vector
        for u in letters:
            U = nibble2vect(level, u, current_vector)
            dist = distance(objective, U)
            if dist < min_dist:
                min_dist = dist
                min_hash = hash + u
                min_U = U
                                    
        # print "dist=" + str(min_dist) + " for " + repr(soln + [min_vect]) 
        if min_dist < epsilon:
            return min_hash
        
        current_error = min_dist
        hash = min_hash
        return refine(objective, epsilon, min_U, current_error, hash)
    

def geohash(x, y, z, epsilon):
    objective = A([x,y,z])
    return refine(objective, epsilon)

# Austin :      ['412504100002014005[0]', '52504100002014005[000]']
# print ecef_geohash(-0.1165684, -0.8572452, 0.501540, 0.001)

# San Antonio : ['412504100000004[00000]', '52504100000004[000000]']
# print ecef_geohash(-0.128860005, -0.862881594, 0.488789934, 0.001)

# Edge condition
#  Two points within 8 km of each other but:
#  ['1', '2113636363636363636']
#  versus
#  ['1', '1122626262626262626']
# print ecef_geohash(e - .0001, e + .0001, 0, 0.001)
# print ecef_geohash(e + .0001, e - .0001, 0, 0.001)

def randomTest():
    offsets = [-0.001, 0.005, 0.005]
    for i in range(10000):
        t = A([ random.random(), random.random(), random.random() ])
        u0 = t / math.sqrt( (t[0]*t[0]) + (t[1]*t[1]) + (t[2]*t[2]) )
        u1 = [ u0[0] + offsets[0], u0[1] + offsets[1], u0[2] + offsets[2] ]
        random.shuffle(offsets)
        h0 = ecef_geohash(u0[0], u0[1], u0[2], 0.001)
        h1 = ecef_geohash(u1[0], u1[1], u1[2], 0.001)
        pfx = [ os.path.commonprefix([h0[0], h1[0]]), os.path.commonprefix([h0[1], h1[1]]) ]
        N = max( len(pfx[0]), len(pfx[1]) )
        if N < 12 :
            print [u0, u1]
            print h0[0]
            print h1[0]
            print h0[1]
            print h1[1]
            
print geohash(0.15373484,  0.99290733,  0.01481033, 0.001)

