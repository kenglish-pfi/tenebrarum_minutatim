import sys, math, numpy, random, os

def A(a):
    return numpy.array(a)

e = 1.0/math.sqrt(2.0)
basi = [
    A([ A([1,0,0]), A([0,1,0]), A([0,0,1]), A([-1,0,0]), A([0,-1,0]), A([0,0,-1]) ]), 
    A([ A([e,e,0]), A([0,e,e]), A([e,0,e]), A([-e,-e,0]), A([0,-e,-e]), A([-e,0,-e]) ])
]
factor = 1.0/math.sqrt(2.0)
skip = A([0,0,0])

def soln_value(soln):
    # print "soln_value(" + repr(soln) + ")"
    accum = [0,0,0]
    for v in soln:
        accum[0] = accum[0] + v[0]
        accum[1] = accum[1] + v[1]
        accum[2] = accum[2] + v[2]
    denom = math.sqrt( (accum[0]*accum[0]) + (accum[1]*accum[1]) + (accum[2]*accum[2]) )
    accum[0] = accum[0] / denom
    accum[1] = accum[1] / denom
    accum[2] = accum[2] / denom
    # print "   SUMMED/NORMED accum:" + repr(accum)
    return A(accum)

def distance(objective, soln):
    pre_dist = objective - soln_value(soln)
    dist = math.sqrt((pre_dist[0]*pre_dist[0]) + (pre_dist[1]*pre_dist[1]) + (pre_dist[2]*pre_dist[2]))
    return dist

def refine(objective, epsilon, orientation, soln=[], current_error=2.0, hash=""):
    N = len(soln)
    if N > 24 :
        print "Failed to converge:"
        print "   refine(" + ", ".join([ repr(objective), str(epsilon), str(orientation), repr(soln), str(current_error), hash]) + ")"
        return hash + "7"
    if (N & 1) == orientation :
        basis = basi[1]
    else:
        basis = basi[0]
    
    if N > 0:
        basis = basis * math.pow(factor, N)
        
    min_dist = 2.0
    min_vect = basis[0]
    min_idx = 0
    for idx in range(6):
        v = basis[idx]
        attempt = soln + [v]
        dist = distance(objective, attempt)
        if dist < min_dist:
            min_dist = dist
            min_vect = v
            min_idx = idx
    
    # print "dist=" + str(min_dist) + " for " + repr(soln + [min_vect]) 
    if min_dist < epsilon:
        hash = hash + str(min_idx+1)
        return hash
    if min_dist > current_error:
        # Skip situation ...
        hash = hash + "0"
        return refine(objective, epsilon, orientation, soln + [A([0,0,0])], current_error, hash)
    
    current_error = min_dist
    hash = hash + str(min_idx+1)
    return refine(objective, epsilon, orientation, soln + [min_vect], current_error, hash)
    

def ecef_geohash(x, y, z, epsilon):
    objective = A([x,y,z])
    return [ refine(objective, epsilon, 0), refine(objective, epsilon, 1) ]

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
            
randomTest()
